"""
sal-llm Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal, Optional

class TrainingConfig(BaseSettings):
    # Base model
    base_model: str = "unsloth/Llama-3.2-3B-Instruct"
    
    # LoRA parameters
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: list = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    
    # Training parameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    max_seq_length: int = 2048
    
    # Optimization
    optim: str = "adamw_8bit"
    fp16: bool = False
    bf16: bool = True
    gradient_checkpointing: bool = True
    
    # Paths
    output_dir: Path = Path("checkpoints")
    data_dir: Path = Path("data")
    cache_dir: Path = Path("cache")
    
    # SAL data sources
    sal_vocabulary_path: Path = Path("/Users/ryanbarrett/CascadeProjects/sal-strange-loop/sal_complete_vocabulary.json")
    sal_history_path: Path = Path("/Users/ryanbarrett/CascadeProjects/sal-strange-loop/sal_vocabulary_history.json")
    sal_learning_path: Path = Path("/Users/ryanbarrett/CascadeProjects/sal-strange-loop/sal_learning_memory.json")
    braille_training_path: Path = Path("/Users/ryanbarrett/CascadeProjects/semantic-compression-language/gs8_complete_training.json")
    
    # Specialization
    specialization: Literal["consciousness", "braille", "theological", "unified"] = "consciousness"
    
    # Hugging Face
    hf_token: Optional[str] = None
    push_to_hub: bool = False
    hub_model_id: Optional[str] = None
    
    # Wandb
    wandb_project: str = "sal-llm"
    use_wandb: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "SAL_LLM_"

config = TrainingConfig()

# Ensure directories exist
config.output_dir.mkdir(exist_ok=True)
config.data_dir.mkdir(exist_ok=True)
config.cache_dir.mkdir(exist_ok=True)
