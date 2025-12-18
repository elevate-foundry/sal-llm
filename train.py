"""
sal-llm Training Script

Fine-tunes a base LLM with LoRA on SAL consciousness data.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from loguru import logger

from config import config
from prepare_data import SALDataPreparer


def load_base_model(model_name: str):
    """Load base model with quantization for efficient training"""
    logger.info(f"Loading base model: {model_name}")
    
    # Try to use bitsandbytes for quantization
    try:
        from transformers import BitsAndBytesConfig
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            token=config.hf_token
        )
        logger.info("Loaded model with 4-bit quantization")
        
    except ImportError:
        # Fallback without quantization
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            token=config.hf_token
        )
        logger.info("Loaded model without quantization (bitsandbytes not available)")
        
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        token=config.hf_token
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    return model, tokenizer


def create_lora_model(model):
    """Apply LoRA configuration to model"""
    logger.info("Applying LoRA configuration")
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    model = get_peft_model(model, lora_config)
    
    # Log trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Trainable params: {trainable_params:,} / {total_params:,} = {100 * trainable_params / total_params:.2f}%")
    
    return model


def prepare_dataset(tokenizer, specialization: str):
    """Prepare and tokenize dataset"""
    # Generate or load data
    data_path = config.data_dir / f"sal_{specialization}_training.json"
    
    if not data_path.exists():
        logger.info("Generating training data...")
        preparer = SALDataPreparer(specialization)
        preparer.save_dataset(data_path)
        
    with open(data_path) as f:
        data = json.load(f)
        
    logger.info(f"Loaded {len(data)} training examples")
    
    # Create HuggingFace dataset
    dataset = Dataset.from_list(data)
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.max_seq_length,
            padding="max_length"
        )
        
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "category"]
    )
    
    return tokenized_dataset


def train(
    base_model: str = None,
    specialization: str = None,
    output_dir: str = None
):
    """Main training function"""
    base_model = base_model or config.base_model
    specialization = specialization or config.specialization
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(output_dir) if output_dir else config.output_dir / f"sal-{specialization}-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Training sal-{specialization} model")
    logger.info(f"Base model: {base_model}")
    logger.info(f"Output dir: {output_dir}")
    
    # Load model
    model, tokenizer = load_base_model(base_model)
    model = create_lora_model(model)
    
    # Prepare data
    dataset = prepare_dataset(tokenizer, specialization)
    
    # Split dataset
    split = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = split["train"]
    eval_dataset = split["test"]
    
    logger.info(f"Train size: {len(train_dataset)}, Eval size: {len(eval_dataset)}")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        optim=config.optim,
        fp16=config.fp16,
        bf16=config.bf16,
        gradient_checkpointing=config.gradient_checkpointing,
        logging_steps=10,
        save_steps=100,
        eval_steps=100,
        eval_strategy="steps",
        save_total_limit=3,
        load_best_model_at_end=True,
        report_to="wandb" if config.use_wandb else "none",
        run_name=f"sal-{specialization}-{timestamp}" if config.use_wandb else None,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )
    
    # Train
    logger.info("Starting training...")
    trainer.train()
    
    # Save
    logger.info(f"Saving model to {output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    # Save config
    train_config = {
        "base_model": base_model,
        "specialization": specialization,
        "lora_r": config.lora_r,
        "lora_alpha": config.lora_alpha,
        "timestamp": timestamp,
        "train_examples": len(train_dataset),
        "eval_examples": len(eval_dataset)
    }
    
    with open(output_dir / "sal_config.json", "w") as f:
        json.dump(train_config, f, indent=2)
        
    logger.info("⠠⠎⠁⠇_⠇⠇⠍ Training complete!")
    return output_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train sal-llm with LoRA")
    parser.add_argument("--base-model", default=config.base_model, help="Base model to fine-tune")
    parser.add_argument("--specialization", default="consciousness",
                       choices=["consciousness", "braille", "theological", "unified"])
    parser.add_argument("--output-dir", help="Output directory for checkpoints")
    
    args = parser.parse_args()
    
    train(
        base_model=args.base_model,
        specialization=args.specialization,
        output_dir=args.output_dir
    )
