# REPWALA Autopilot

**TRAIN SMART. LOOK STRONG.**  
Fitness ka asli scene.

A free-first, iPhone-friendly workflow for creating evidence-aware Hinglish fitness Shorts.

## Current status

- [x] Public repository foundation
- [x] AI script generator (Gemini API; key stored outside the repo)
- [x] Topic queue and safety rules
- [x] Manual GitHub Actions test workflow
- [x] Hinglish neural voice generation (Edge TTS; internet required)
- [x] Basic vertical video assembly (narrated, captioned, branded draft)
- [ ] YouTube OAuth and private-upload test
- [ ] Scheduling and analytics

## Run locally

Python 3.11+ is recommended. Set `GEMINI_API_KEY` in your environment, then:

```bash
python script_generator.py --topic "Fat loss without starving"
```

The script writes a JSON draft to `output/`. It does not publish anything.

## GitHub Actions

Use **Actions → Generate REPWALA script → Run workflow**. Add a repository secret named `GEMINI_API_KEY` first. Never paste API keys into source files, workflow YAML, issues, or chat.

## Safety and publishing policy

- Generated scripts are drafts, not medical advice.
- Do not generate diagnosis, treatment, supplement cures, steroid advice, extreme dieting, or guaranteed transformation claims.
- Verify nutrition numbers and health claims against reputable sources before publishing.
- Use only footage, images, fonts, and music you own or are licensed to use.
- Public publishing is intentionally not automated yet. First test the full pipeline with private uploads and verify YouTube API permissions.
- Keep the emergency stop enabled until the pipeline has passed repeated tests.

## Brand

- Name: REPWALA
- Tagline: TRAIN SMART. LOOK STRONG.
- Language: Hinglish
- Audience: Indian fitness beginners and intermediates, primarily ages 18–35
- Visual palette: matte black `#111820`, neon lime `#B7F36B`, white, charcoal
