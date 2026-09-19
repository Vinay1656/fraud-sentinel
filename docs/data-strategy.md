# Data strategy

The three original hackathon CSVs remain local. They contain customer information and are not redistributed in the public repository. Public demos use fictional records created by `scripts/create_demo_data.py`.

The existing model uses 512 synthetic training scenarios and a separate 128-example synthetic holdout. A separate seed prevents exact row overlap but does not create an independent real-world benchmark. New data work must improve scenario coverage and evaluation independence, not just increase row counts.

Candidate sources and a concrete expansion plan will be recorded at the next planning checkpoint. External data will keep its own provenance, labels, feature mapping, and license information; missing fields will not be presented as observed facts.
