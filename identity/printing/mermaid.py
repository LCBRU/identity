from identity.setup.studies import StudyName
from .model import LabelPack
from .briccs import BriccsBags


class MermaidPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'MermaidPack',
    }

    __study_name__ = StudyName.MERMAID

    def _do_print(self):
        bb = BriccsBags()
        participant_id = bb.print_pack(
            study_name='MERMIAD 1',
            additional_sample_label_count=4,
        )
        self.save_participant_id(participant_id)
