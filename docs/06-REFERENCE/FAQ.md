# Frequently Asked Questions

**Version:** 1.0

---

## General

**Q: What is VIRA?**  
A: Venture Intelligence Research Assistant - AI platform analyzing business plan alignment with VC investment criteria.

**Q: Who is it for?**  
A: Early-stage founders (18-36 months pre-fundraising) and VC analysts screening deal flow.

**Q: How accurate is it?**  
A: 70-90% agreement with human analysts (depending on iteration). Always verify critical decisions.

---

## Technical

**Q: What LLM does VIRA use?**  
A: GPT-4o-mini for cost-efficiency. Can be swapped for GPT-4 for higher quality.

**Q: How much does each analysis cost?**  
A: ~$0.002-0.05 (Iter 1), ~$0.05-0.15 (Iter 2), ~$0.30-0.80 (Iter 3 planned).

**Q: Can I use my own VC firm content?**  
A: Yes! Update `config/crawl_settings.yaml` with your firm's URLs and re-run crawler.

**Q: How often should I update VC content?**  
A: Monthly recommended. Run: `python -m vira.ingestion.runner crawl ...`

**Q: Can I run VIRA offline?**  
A: No, requires OpenAI API (cloud-based LLM). Future: local LLM support via Ollama.

---

## Usage

**Q: What file formats are supported?**  
A: PDF, DOCX, TXT for business plans.

**Q: How long does analysis take?**  
A: 3-5s (Iter 1), 15-30s (Iter 2), 20-40s (Iter 3 planned).

**Q: Can I save and compare versions?**  
A: Yes! Use `/versions` command in Chainlit UI to see all plan versions.

**Q: Can multiple users use VIRA simultaneously?**  
A: Yes, prototype supports ~10-50 concurrent users. Production: scale horizontally.

---

## Troubleshooting

**Q: "Import Error: No module named vira"**  
A: Install package: `pip install -e .`

**Q: "OpenAI API Error: Insufficient quota"**  
A: Add payment method to OpenAI account or check API key.

**Q: Analysis takes >1 minute**  
A: Likely Iteration 2 with many research queries. Check `SERPER_API_KEY` and network.

**Q: "No documents retrieved"**  
A: Vector DB may be empty. Run: `python -m vira.processing.cli ingest ...`

---

**More questions?** See documentation or contact team.
