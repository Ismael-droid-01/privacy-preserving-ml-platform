## PRIVACY PRESERVING ML PLATFORM
- `client`: Angular client.
- `test`: Test code used only for learning and pre-development purposes.
- `preprocess_server`: Data encryption service.
- `ppml_server`: Service for running machine learning algorithms while preserving privacy.
---
## Execution
The `start` command contains bash instructions for running any of the following servers and can be executed as follows:

**Angular Client**
```bash
./start -c
```
**Preprocess Server**
```bash
./start -p
```
**PPML Server**
```bash
./start -m
```