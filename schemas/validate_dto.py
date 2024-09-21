from pydantic import BaseModel

from schemas.tb_ka_message_dto import TbKaMessageDto


class ValidateDto:
    class ValidateReqDto(BaseModel):
        chat_id: int
        client_message_id: int
        room_id: int
        user_id: int
        message: str
        sent_at: int

        def to_save_req_dto(self, additional_fields: TbKaMessageDto.AdditionalFieldServDto) -> TbKaMessageDto.SaveReqDto:
            return TbKaMessageDto.SaveReqDto(
            room_id = self.room_id,
            chat_id = self.chat_id,
            client_message_id = self.client_message_id,
            user_id = self.user_id,
            subject_id = additional_fields.subject_id,
            message = self.message,
            threshold = additional_fields.threshold,
            distance = additional_fields.distance,
            similar_id = additional_fields.similar_id,
            last_sent_at = self.sent_at,
        )


    class ValidateResDto(BaseModel):
        message_id: str
        chat_id: int
        message: str
        subject_id: int

    class GetDistanceServDto(BaseModel):
        message: str
        n_similar: int

    class DistanceSimilarItemServDto(BaseModel):
        distances: list
        similar_items: list
