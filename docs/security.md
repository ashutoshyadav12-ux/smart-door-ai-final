# Security & privacy
- **Fail-secure:** errors, low quality, unknown face, lockout → locked.
- **Biometric data:** only 512-d embeddings (not photos) are used for matching; cropped samples in `data/faces` are optional—delete them for privacy. Deleting a user cascades to all their embeddings.
- **Liveness is a prototype** (blink/motion) and can be defeated by video replay. Use depth/IR for real protection; don't secure anything valuable with this alone.
- **Lockout + cooldown** limit brute-force attempts; every decision is audited in `AccessLog`.
- **Secrets:** set strong `SECRET_KEY`, `ADMIN_PASSWORD`, `DEVICE_API_KEY`; serve over HTTPS; add MQTT auth + TLS beyond a LAN demo.
- Get consent before enrolling anyone's face and follow local biometric-data law.
