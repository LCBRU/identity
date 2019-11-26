from .model import LabelPack
from .briccs import BriccsBags


class MermaidPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'MermaidPack',
    }

    __study_name__ = 'MERMAID'

    def print(self):
        bb = BriccsBags()
        bb.print_pack(
            study_name='MERMIAD 1',
            additional_sample_label_count=4,
        )
