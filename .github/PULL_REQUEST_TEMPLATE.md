# 🧠 Asyncio Plugin – Pull Request

Thank you for contributing to the Asyncio Limnoria plugin.

Please complete the checklist below before requesting review.

---

## 📋 Summary

Briefly describe the purpose of this pull request.

- What problem does it solve?
- What feature does it add?
- What behaviour does it change?

---

## 🔧 Type of Change

Please tick one:

- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 🛠 Refactor
- [ ] 📖 Documentation update
- [ ] ⚙️ Configuration change
- [ ] 🔒 Security improvement

---

## 🧪 Testing Performed

Describe how this change was tested.

- [ ] Tested in single channel
- [ ] Tested in multiple channels
- [ ] Tested via private message
- [ ] Tested cooldown behaviour
- [ ] Tested moderation behaviour
- [ ] Tested math mode output (≤ 6 lines)
- [ ] Verified no history cross-contamination
- [ ] Verified no IRC truncation

If applicable, include sample commands and outputs:
!chat Example test input

---

## 🧠 Memory & Context Safety

Confirm:

- [ ] No reintroduction of global conversation history
- [ ] Context key logic (`channel:nick`) remains intact
- [ ] History trimming still enforced

---

## ⚡ Async & Thread Safety

Confirm:

- [ ] No changes interfere with `threaded = True`
- [ ] No direct event loop manipulation added
- [ ] `asyncio.run()` usage remains safe

---

## 🔢 Token & Output Handling

Confirm:

- [ ] Token limit enforcement still active
- [ ] IRC chunking preserved
- [ ] No LaTeX formatting leaks into IRC output

---

## 📖 Documentation Updated

If relevant:

- [ ] README updated
- [ ] CHANGELOG updated
- [ ] DEVELOPER_NOTES updated

---

## 📝 Additional Notes

Add any extra context here.
