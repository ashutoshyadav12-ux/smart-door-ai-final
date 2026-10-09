# 12-step demo walkthrough
1. Open the dashboard URL, log in as admin.
2. Show Dashboard: door **locked**, zeros in metrics.
3. Users → **Add user** "Demo Student".
4. Click **Enroll** → start camera.
5. Capture 5 samples following the on-screen prompts (progress bar → 5/5).
6. Live Recognition → start camera → **Start scanning**.
7. Enrolled face → ✅ "Welcome", door shows **unlocked** with countdown, auto-relocks.
8. Show an unknown face/photo of someone else → ⛔ unknown.
9. Settings → raise the threshold, re-test; enable liveness (prototype) and explain its limits.
10. Trigger repeated failures → lockout message.
11. Access Logs → filter GRANTED vs UNKNOWN, search by name.
12. IoT Devices → manual Lock/Unlock, explain demo vs ESP32/MQTT mode.
