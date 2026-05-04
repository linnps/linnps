<div align="center">

<a href="https://github.com/linnps">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=28&duration=2400&pause=900&color=3B6EA8&center=true&vCenter=true&width=720&lines=Reference+implementations+of+the+ML+curriculum;Synthetic+data+with+known+ground+truth;Dashboards+over+benchmark+numbers" alt="header" />
</a>

### Purdue PhD · UIUC CS · several years of engineering experience

</div>

---

## 👋 About

Engineer with a research-science background — a Purdue PhD followed
by graduate CS work at UIUC — and a multi-year track record of
shipping ML and engineering systems in industry. The repos linked
here put that experience to a different use: distilling the canonical
machine-learning curriculum into a series of small, well-instrumented
**reference implementations** that other people can read, run, and
modify.

Each one picks a single canonical topic, strips it down to its
essential moving parts, and explains it through code and
visualizations rather than equations and prose.

> 🔭 &nbsp;**Currently** — turning the major branches of ML into reference projects, one repo per topic
>
> 🛠️ &nbsp;**Background** — research science · applied ML engineering · production systems · technical mentoring
>
> ⚡ &nbsp;**Approach** — synthetic data with known ground truth · code that reads like an explanation · dashboards designed to be scanned in 30 seconds
>
> 💬 &nbsp;**Useful for** — anyone who wants a particular ML concept implemented end-to-end, without the usual benchmark-fetishism

These projects are deliberately small. The goal isn't state-of-the-art
numbers — it's to make every step of a working ML pipeline **visible,
modifiable, and teachable**. If they help someone go from *"I've read
the paper"* to *"I can build it from scratch,"* they've done their job.

---

## What's in the repo list

A reference set covering the major branches of machine learning —
one project per topic, each one self-contained and built to the
same recipe so the boilerplate is invisible and the *content* is
what stands out:

- A synthetic data generator with a **known generative process** — so models can be evaluated against the *truth*, not just a holdout score
- A from-scratch implementation in PyTorch or scikit-learn — minimal dependencies, readable top-to-bottom
- A dashboard-style README with embedded charts in a unified palette
- A *"What I learned"* reflection at the end — not a metrics dump

<table>
<tr>
<th align="left">Topic</th>
<th align="left">Demonstrated skills</th>
</tr>
<tr><td><b>Supervised — regression</b></td>
<td>OLS · Ridge · Lasso · coefficient-recovery diagnostics</td></tr>
<tr><td><b>Supervised — classification</b></td>
<td>Logistic · Decision Tree · Random Forest · Gradient Boosting</td></tr>
<tr><td><b>Unsupervised — clustering</b></td>
<td>K-means · DBSCAN · Agglomerative · ARI vs Silhouette</td></tr>
<tr><td><b>Unsupervised — dim reduction</b></td>
<td>PCA · t-SNE · trustworthiness · scree plots</td></tr>
<tr><td><b>Deep learning — vision</b></td>
<td>CNN from scratch · PyTorch · synthetic image rendering</td></tr>
<tr><td><b>Deep learning — sequence</b></td>
<td>LSTM · time-series forecasting · seasonal-naive baselines</td></tr>
<tr><td><b>Deep learning — NLP</b></td>
<td>Transformer encoder from scratch · attention visualization</td></tr>
<tr><td><b>Modern AI — LLM</b></td>
<td>RAG · vector retrieval · refusal-threshold tuning · hallucination measurement</td></tr>
<tr><td><b>Production / MLOps</b></td>
<td>FastAPI · Docker · PSI / KS drift monitoring · latency probing</td></tr>
<tr><td><b>Reinforcement learning</b></td>
<td>DQN · replay buffer · target network · ε-greedy schedule</td></tr>
</table>

---

## Other repositories

A short tour of the older public repos on this profile — they pre-date
the current ML focus and span device-physics simulation, deep-learning
research, full-stack web services, a desktop application, and IoT /
robotics. Together they show the breadth of programming work behind the
ML reference set above.

### Semiconductor device simulation — TCAD (Silvaco Athena/Atlas)

Numerical simulations of canonical device structures: process flow,
electrostatic field, carrier concentration, and IV-curve sweeps —
rendered for each device type.

- [TCAD — Diode](https://github.com/linnps/TCAD-Simulation-Diode)
- [TCAD — MOSFET](https://github.com/linnps/TCAD-Simulation-MOSFET)
- [TCAD — BJT](https://github.com/linnps/TCAD-Simulation-Bipolar-Junction-Transistor-BJT)
- [TCAD — FinFET](https://github.com/linnps/TCAD-simulation-fin-field-effect-transistor-FinFET)

> **Skills demonstrated:** semiconductor device physics · process / device simulation · electrostatic & carrier-transport solvers · IV-curve interpretation

### Deep-learning research

- [**Heart-failure risk prediction (DG-RNN on MIMIC-III)**](https://github.com/linnps/DLH_Team38_Final) — Domain-Knowledge-Guided Recurrent Neural Network with knowledge-graph features, comparing against standard EHR risk-prediction models. PyTorch + PyHealth. Coursework for *Deep Learning for Healthcare* (UIUC CS 598).

> **Skills demonstrated:** PyTorch · RNN / GRU on irregular time-stamped sequences · knowledge-graph integration · PyHealth · clinical EHR data handling

### Web / backend services

- [**RESTful API from scratch**](https://github.com/linnps/Self-made-RESTful-API) — Express + MongoDB; full GET / PUT / PATCH / DELETE article CRUD; tested via Postman.
- [**Online to-do list service**](https://github.com/linnps/Online-to-do-list-service) — Node.js + MongoDB on Heroku, with per-user collections and weather / location enrichment.
- [**Newsletter sign-up service**](https://github.com/linnps/Newsletter-Online-Sign-Up-Service) — Node.js + MailChimp on Heroku.

> **Skills demonstrated:** Node.js · Express · REST API design · MongoDB · third-party API integration · cloud deployment

### Desktop application

- [**Web Browser — three-tier C# desktop app**](https://github.com/linnps/Web-Browser-three-tier-graphical-event-driven-desktop-application) — Object-oriented event-driven browser with bookmark / history managers backed by SQL. Built incrementally from a single button to a full multi-tab application.

> **Skills demonstrated:** OOP · C# / WinForms · event-driven UI · multi-tier architecture · SQL persistence

### IoT / robotics

- [**Self-driving car — environment scanning + autonomous driving**](https://github.com/linnps/iot-sp2022-lab1) — Lab for *IoT Systems* (UIUC CS 437). Mapping the local environment and driving around obstacles.

> **Skills demonstrated:** IoT pipelines · sensor data processing · simple autonomous control loops

---

## Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=python,pytorch,sklearn,fastapi,docker,git,github,bash,vscode,linux&perline=10" alt="stack" />

</div>

**Comfortable with**
&nbsp;&nbsp; `Python` &nbsp;·&nbsp; `PyTorch` &nbsp;·&nbsp; `scikit-learn` &nbsp;·&nbsp; `pandas` &nbsp;·&nbsp; `NumPy` &nbsp;·&nbsp; `matplotlib` &nbsp;·&nbsp; `FastAPI` &nbsp;·&nbsp; `Docker` &nbsp;·&nbsp; `Git`

**Working knowledge**
&nbsp;&nbsp; `SQL` &nbsp;·&nbsp; `Bash` &nbsp;·&nbsp; `JavaScript / TypeScript` &nbsp;·&nbsp; `Hugging Face transformers` &nbsp;·&nbsp; `Linux`

---

## Principles these repos are written to

> *"Synthetic data first.  Dashboards over benchmarks.  Boring code, sharp insights.  Always end with what was learned."*

- **Synthetic data first.** When the generative process is known, models can be evaluated against the *truth*, not just a holdout number. Coefficient recovery, ground-truth ARI, theoretical noise floors — diagnostics that benchmark datasets cannot offer.
- **Dashboards over benchmarks.** Every project ends with figures a reader can scan in 30 seconds, not a single F1 score buried in a table.
- **Boring code, sharp insights.** Code prioritizes clarity over cleverness. The interesting part lives in the analysis and visualizations, not in the lines themselves.
- **Reflection beats reporting.** Metrics describe what happened. *"What I learned"* sections describe what I would do differently next time — and that's the part worth keeping six months later.

---

## Stats

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=linnps&show_icons=true&hide_border=false&border_color=E5E5E5&title_color=3B6EA8&icon_color=C04040&text_color=333333&bg_color=FFFFFF&include_all_commits=true&count_private=true&rank_icon=github" alt="GitHub Stats" height="170" />
&nbsp;
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=linnps&layout=compact&hide_border=false&border_color=E5E5E5&title_color=3B6EA8&text_color=333333&bg_color=FFFFFF&langs_count=8" alt="Top Languages" height="170" />

<br/>
<br/>

<img src="https://streak-stats.demolab.com?user=linnps&hide_border=false&border=E5E5E5&background=FFFFFF&stroke=E5E5E5&ring=3B6EA8&fire=C04040&currStreakLabel=3B6EA8&sideLabels=333333&dates=7A7A7A&currStreakNum=333333&sideNums=333333&dayNum=333333" alt="Streak" height="170" />

</div>

---

<div align="center">
<sub>Palette: <code>#3B6EA8</code> blue · <code>#C04040</code> red · <code>#7A7A7A</code> gray · <code>#E5E5E5</code> light gray · <code>#FFFFFF</code> white &nbsp;·&nbsp; the same one used across every project.</sub>
</div>
