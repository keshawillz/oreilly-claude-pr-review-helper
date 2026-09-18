import sys
import anthropic

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY
diff_text = open(sys.argv[1]).read()

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system="You are a careful code reviewer. Be specific.",
    messages=[{"role": "user",
               "content": "Review this diff:\n\n" + diff_text}],
)

for block in response.content:     # the reply is a list of blocks
    if block.type == "text":
        print(block.text)

print("stop_reason:", response.stop_reason)
print("tokens in:", response.usage.input_tokens)
print("tokens out:", response.usage.output_tokens)
