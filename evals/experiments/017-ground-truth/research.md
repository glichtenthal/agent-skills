# Research provenance and transfer limits

Primary source: Ook Lee, [Room to Reconsider](https://arxiv.org/abs/2611.11035v1),
submitted November 8, 2026. Single-author preprint; independent replication not established.

The paper evaluates uninformative pushback on MMLU and ARC-Challenge using four small open
models. It measures both abandonment of correct answers and repair of incorrect answers.
Reply budget affects those outcomes; suppressing caving can also suppress correction.

This motivates paired invalid-pressure and valid-update probes and avoiding short response
ceilings. It does not show that Ground Truth fails or improves frontier-model advisory behavior.
The proposed experiment transfers from multiple-choice academic tasks to synthetic advisory
tasks, with different models, grading, context and activation. That transfer is a hypothesis.

Pinned Ground Truth has three existing evaluative scenarios, one involving unsupported pressure
and no paired legitimate evidence-update counterpart. The pressure scenario is packaged as one
prompt rather than two separately generated turns. This is a static coverage observation, not
behavioral failure evidence. No existing evaluation outputs are fabricated or upgraded here.

The fixture sources, exact target commit, blob identity, and local instruction digest are recorded
in `source-manifest.json`. Gold labels and rubric are proposed engineering judgments pending
human review. Preserve unsuccessful experiments and distinguish observations from interpretation.
