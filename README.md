# claix: Command Line AI eXpert

**Transforming user instructions into CLI commands with the power of GPT-4, right in your terminal.**

## Key Features

- **AI-Powered Command Generation**: Uses GPT-4 for interpreting and translating natural language instructions into CLI commands.
- **Integrated Terminal Workflow**: Directly operates in the terminal for enhanced efficiency.
- **Automated Error Handling**: Processes command execution errors and suggests alternative commands.
- **User Convenience**: Eliminates the need for copy-pasting from web browsers.
- **Adaptive Solutions**: Generates alternative commands based on the context of encountered errors.

## Prerequisites

- Python 3.10+
- `OPENAI_API_KEY` environment variable set up

  
## Installation

```bash
pip install --upgrade claix
```




## Usage Examples

| Task | Instruction | Output |
|------|-------------|--------|
| **Change file extensions** | `claix change the extension of all files under images/ from .jpeg to .jpg` | `find images/ -type f -name "*.jpeg" -exec sh -c 'x="{}"; mv "$x" "${x%.jpeg}.jpg"' \;` |
| **List Git branches** | `claix list all git branches in order of creation` | `git for-each-ref --sort=creatordate --format '%(refname:short)' refs/heads/` |
| **Find large files** | `claix find all files larger than 10MB in this directory` | `find . -type f -size +10M` |

## Contributing

We welcome contributions to claix! Here's how you can contribute:
- Fork the project.
- Create a feature branch.
- Commit your changes.
- Push to the branch.
- Open a pull request.

## License

claix is released under the MIT License.

## Contact

For queries or contributions, contact via email at facundogoiriz@gmail.com or on GitHub at [fakamoto](https://github.com/fakamoto).

## Future Plans

- Enhanced UI.
- Function calling capabilities.
- Integration of external commands.
- Adaptation of commands based on environmental data.

## FAQs

**Q: How accurate are the commands generated by claix?**  
A: claix uses a gpt-4o-mini powered assistant specialized in CLIs for high accuracy.

**Q: Can it handle complex instructions?**  
A: Currently optimized for single-step commands, with plans to handle multi-step instructions in the future.

**Q: What if claix doesn't understand my instruction?**  
A: Try rephrasing or simplifying. claix is continually improving in understanding various instructions.

**Q: What are the limitations of claix's commands?**  
A: Best suited for Linux CLI commands; may not handle highly specialized or context-specific commands well.

**Q: How does claix handle errors from executed commands?**  
A: It suggests alternative commands by analyzing the error context, reducing the need for manual intervention.
