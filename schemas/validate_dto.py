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

        def to_save_req_dto(self, subject_id: int) -> TbKaMessageDto.SaveReqDto:
            return TbKaMessageDto.SaveReqDto(
            chat_id = self.chat_id,
            client_message_id = self.client_message_id,
            room_id = self.room_id,
            last_sent_at = self.sent_at,
            user_id = self.user_id,
            message = self.message,
            subject_id = subject_id,
        )


    class ValidateResDto(BaseModel):
        message_id: str
        is_duplicate: bool
        subject_id: int

    class GetDistanceServDto(BaseModel):
        message: str
        n_similar: int

    class DistanceSimilarItemServDto(BaseModel):
        distances: list
        similar_items: list

    class UpdateDuplicateMessageServDto(BaseModel):
        chat_id: int
        client_message_id: int
        room_id: int
        user_id: int
        message: str
        sent_at: int
        subject_id: int
