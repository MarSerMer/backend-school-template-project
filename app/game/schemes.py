# from marshmallow import Schema, fields
#
# class GameListSchema(Schema):
#     id = fields.Int()
#     chat_id = fields.Int()
#     captain = fields.Int()
#     players = relationship("UserModel", secondary="game_user")
#     finished = Column(String, default="Not finished")
#     winner = Column(String, default="No winner")
#     players_count = Column(Integer, default=0)
#     bot_count = Column(Integer, default=0)
#     questions = relationship("QuestionModel", secondary="game_question")
