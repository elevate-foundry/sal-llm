"""
Generate programming language training data for SAL in 8-dot braille
"""

import sys
import json
from pathlib import Path

# Add sal-voice to path for braille8_code
sys.path.insert(0, str(Path.home() / "sal-voice"))

from braille8_code import generate_code_training_data, braille_code_encoder, Language

def main():
    print("⠠⠎⠁⠇ Generating code-in-braille training data...")
    
    # Generate base training data
    training_data = generate_code_training_data()
    
    # Add more comprehensive examples
    additional_examples = []
    
    # Python patterns
    python_patterns = [
        "def greet(name: str) -> str:\n    return f'Hello, {name}!'",
        "class Person:\n    def __init__(self, name: str, age: int):\n        self.name = name\n        self.age = age",
        "async def fetch_data(url: str) -> dict:\n    async with aiohttp.ClientSession() as session:\n        return await session.get(url)",
        "[x**2 for x in range(10) if x % 2 == 0]",
        "lambda x, y: x + y",
        "with open('file.txt', 'r') as f:\n    content = f.read()",
        "@decorator\ndef my_function():\n    pass",
        "try:\n    result = risky_operation()\nexcept Exception as e:\n    logger.error(e)",
    ]
    
    # Rust patterns
    rust_patterns = [
        "fn greet(name: &str) -> String {\n    format!(\"Hello, {}!\", name)\n}",
        "struct Person {\n    name: String,\n    age: u32,\n}",
        "impl Person {\n    fn new(name: &str, age: u32) -> Self {\n        Self { name: name.to_string(), age }\n    }\n}",
        "let result: Result<i32, Error> = Ok(42);",
        "match option {\n    Some(value) => value,\n    None => default,\n}",
        "vec![1, 2, 3].iter().map(|x| x * 2).collect::<Vec<_>>()",
        "#[derive(Debug, Clone)]\npub struct MyStruct {}",
        "async fn fetch() -> Result<(), Box<dyn Error>> {\n    Ok(())\n}",
    ]
    
    # Go patterns
    go_patterns = [
        "func greet(name string) string {\n    return fmt.Sprintf(\"Hello, %s!\", name)\n}",
        "type Person struct {\n    Name string `json:\"name\"`\n    Age  int    `json:\"age\"`\n}",
        "func (p *Person) GetName() string {\n    return p.Name\n}",
        "result, err := doSomething()\nif err != nil {\n    return err\n}",
        "go func() {\n    result <- process(data)\n}()",
        "select {\ncase msg := <-ch:\n    handle(msg)\ncase <-ctx.Done():\n    return\n}",
        "defer file.Close()",
        "for i, v := range slice {\n    fmt.Printf(\"%d: %v\\n\", i, v)\n}",
    ]
    
    # JavaScript patterns
    js_patterns = [
        "const greet = (name) => `Hello, ${name}!`;",
        "class Person {\n    constructor(name, age) {\n        this.name = name;\n        this.age = age;\n    }\n}",
        "async function fetchData(url) {\n    const response = await fetch(url);\n    return response.json();\n}",
        "const doubled = [1, 2, 3].map(x => x * 2);",
        "const { name, age } = person;",
        "export default function Component({ props }) {\n    return <div>{props.children}</div>;\n}",
        "try {\n    JSON.parse(data);\n} catch (e) {\n    console.error(e);\n}",
        "const promise = new Promise((resolve, reject) => {\n    setTimeout(() => resolve('done'), 1000);\n});",
    ]
    
    # SQL patterns
    sql_patterns = [
        "SELECT u.name, COUNT(o.id) as order_count\nFROM users u\nLEFT JOIN orders o ON u.id = o.user_id\nGROUP BY u.id\nHAVING COUNT(o.id) > 5\nORDER BY order_count DESC;",
        "INSERT INTO users (name, email, created_at)\nVALUES ('John', 'john@example.com', NOW());",
        "UPDATE products SET price = price * 1.1 WHERE category = 'electronics';",
        "DELETE FROM sessions WHERE last_active < DATE_SUB(NOW(), INTERVAL 30 DAY);",
        "CREATE INDEX idx_users_email ON users(email);",
        "WITH active_users AS (\n    SELECT * FROM users WHERE active = true\n)\nSELECT * FROM active_users;",
        "CASE WHEN score >= 90 THEN 'A'\n     WHEN score >= 80 THEN 'B'\n     ELSE 'C'\nEND AS grade",
    ]
    
    # Java patterns
    java_patterns = [
        "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}",
        "public interface Callable<T> {\n    T call() throws Exception;\n}",
        "List<String> names = Arrays.asList(\"Alice\", \"Bob\", \"Charlie\");",
        "names.stream().filter(n -> n.startsWith(\"A\")).collect(Collectors.toList());",
        "@Override\npublic String toString() {\n    return String.format(\"Person[name=%s]\", name);\n}",
        "Optional<String> result = Optional.ofNullable(getValue());",
        "CompletableFuture.supplyAsync(() -> fetchData())\n    .thenApply(data -> process(data))\n    .exceptionally(e -> handleError(e));",
    ]
    
    patterns_by_lang = [
        (python_patterns, "python"),
        (rust_patterns, "rust"),
        (go_patterns, "go"),
        (js_patterns, "javascript"),
        (sql_patterns, "sql"),
        (java_patterns, "java"),
    ]
    
    for patterns, lang in patterns_by_lang:
        for code in patterns:
            braille = braille_code_encoder.encode(code)
            additional_examples.append({
                "instruction": f"Write this {lang} code in 8-dot braille:",
                "input": code,
                "output": braille,
                "category": f"code_braille_{lang}"
            })
            additional_examples.append({
                "instruction": f"SAL, show me how you think about this {lang} code in braille:",
                "input": code,
                "output": f"I process this {lang} code in my internal 8-dot braille representation:\n\n{braille}\n\nThis is how I 'see' the code - as tactile braille patterns that I can reason about.",
                "category": f"sal_code_thinking_{lang}"
            })
    
    # Combine all training data
    all_data = training_data + additional_examples
    
    # Format for training
    formatted = []
    for ex in all_data:
        if ex.get("input"):
            text = f"### Instruction:\n{ex['instruction']}\n\n### Input:\n{ex['input']}\n\n### Response:\n{ex['output']}"
        else:
            text = f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['output']}"
        formatted.append({
            "text": text,
            "category": ex.get("category", "code_braille")
        })
    
    # Save
    output_dir = Path("training_data")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "sal_code_braille_training.json"
    
    with open(output_path, "w") as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated {len(formatted)} code-in-braille training examples")
    print(f"✓ Saved to {output_path}")
    
    # Print stats by language
    print("\nExamples by language:")
    for lang in Language:
        count = sum(1 for ex in all_data if lang.value in ex.get("category", ""))
        if count > 0:
            print(f"  - {lang.value}: {count}")
    
    return output_path


if __name__ == "__main__":
    main()
