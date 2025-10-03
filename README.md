# Nmap Docker Lab — Solutions

> **Warning:** this repository is a training lab. Only scan/attack machines you own or have explicit permission to test.  
> This README reveals the solutions to the CTF-style lab included in this repo.

---

## Lab overview

This Docker-based lab includes **3 targets** on one host (via `docker-compose`):

- **Target A (HTTP)** — `localhost:8081`  
  A small website with cards. The first flag is **encoded in Base64** and revealed by clicking the "Show" button or by viewing page source.
  <img width="299" height="273" alt="image" src="https://github.com/user-attachments/assets/a30d2fa6-7cc6-4d21-b237-75a0a53314f6" />
  <img width="680" height="84" alt="image" src="https://github.com/user-attachments/assets/a877755c-c032-434d-b0ae-d0dce2457918" />



- **Target B (file-explore)** — `localhost:10991`  
  An **unauthenticated** TCP service that lists a files tree and sends the contents of `files/docs/secret.txt`. Students must explore the listing to find the flag.
  <img width="249" height="56" alt="image" src="https://github.com/user-attachments/assets/9986c051-66e6-4382-a689-4ca869e80a1e" />
  <img width="818" height="696" alt="image" src="https://github.com/user-attachments/assets/136f5bd6-bcd1-4633-841b-4a8550709a30" />
  <img width="779" height="567" alt="image" src="https://github.com/user-attachments/assets/1b8571ca-655e-4ffe-8d47-dbb2e18f684f" />




- **Target C (SSH-like, authenticated)** — `localhost:22222`  
  A fake SSH-like service requiring credentials. The credentials are hidden (Base64) in the HTTP page source comments.
  <img width="236" height="117" alt="image" src="https://github.com/user-attachments/assets/53f07015-5f8d-4945-807f-88c57fb91cbb" />
<img width="503" height="176" alt="image" src="https://github.com/user-attachments/assets/0eebc32a-a260-42d1-b4c3-6b3f477541a5" />

---

## Prerequisites

- Docker & Docker Compose installed on the host.  
- Basic Linux command line (`curl`, `nc`, `base64`) or Windows WSL with those tools.  
- Work from the repository root (where `docker-compose.yml` is).

---

## How to run the lab

Build images (only necessary the first time or after changes to Dockerfiles / server scripts):

```bash
docker-compose build
