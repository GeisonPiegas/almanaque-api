from enum import StrEnum


class ReportReasons(StrEnum):
    SIMPLY_DISLIKED = "SIMPLY_DISLIKED"  # Simplesmente não gostei
    BULLYING_OR_UNWANTED_CONTACT = "BULLYING_OR_UNWANTED_CONTACT"  # Bullying ou contato indesejado
    SUICIDE_SELF_HARM_OR_EATING_DISORDERS = (
        "SUICIDE_SELF_HARM_OR_EATING_DISORDERS"  # Suicídio, automutilação ou distúrbios alimentares
    )
    VIOLENCE_HATE_OR_EXPLOITATION = "VIOLENCE_HATE_OR_EXPLOITATION"  # Violência, ódio ou exploração
    SALE_OR_PROMOTION_OF_RESTRICTED_ITEMS = (
        "SALE_OR_PROMOTION_OF_RESTRICTED_ITEMS"  # Venda ou promoção de itens restritos
    )
    NUDITY_OR_SEXUAL_ACTIVITY = "NUDITY_OR_SEXUAL_ACTIVITY"  # Nudez ou atividade sexual
    SCAM_FRAUD_OR_SPAM = "SCAM_FRAUD_OR_SPAM"  # Golpe, fraude ou spam
    MISINFORMATION = "MISINFORMATION"  # Informação falsa


REPORT_REASONS = tuple((e.value, e.name) for e in ReportReasons)


class ReportStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


REPORT_STATUS = tuple((e.value, e.name) for e in ReportStatus)
