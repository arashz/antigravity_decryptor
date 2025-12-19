# Contributing to Antigravity Decryptor

First off, thank you for considering contributing to Antigravity Decryptor! 🎉

## How Can I Contribute?

### 🐛 Reporting Bugs

Found a bug? Please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version)
- Any relevant error messages or logs

### 💡 Suggesting Enhancements

Have an idea for improvement? We'd love to hear it!
- Open an issue with the "enhancement" label
- Clearly describe the feature and its benefits
- Include examples of how it would be used

### 📝 Improving Documentation

Documentation improvements are always welcome:
- Fix typos or clarify confusing sections
- Add more examples
- Improve installation instructions
- Update outdated information

### 🔧 Contributing Code

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Keep changes focused and atomic
4. **Test your changes**
   ```bash
   python antigravity_decrypt.py --help
   # Test with actual files if possible
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## Code Style Guidelines

- Follow PEP 8 for Python code style
- Use descriptive variable and function names
- Add docstrings for functions and classes
- Keep functions focused on a single task
- Use type hints where appropriate

## Adding Examples

Have a useful example? Add it to the `examples/` directory:
1. Create a well-commented script
2. Add documentation to `examples/README.md`
3. Make scripts executable: `chmod +x yourscript.py`
4. Test thoroughly before submitting

## Testing

Before submitting a PR:
1. Test basic functionality:
   ```bash
   python antigravity_decrypt.py --help
   python antigravity_decrypt.py --version
   python antigravity_decrypt.py --interactive
   ```
2. Test with actual conversation files if available
3. Check that error messages are helpful and accurate
4. Verify documentation is up to date

## Questions?

Feel free to open an issue if you have questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making Antigravity Decryptor better! 🚀
