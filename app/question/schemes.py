from marshmallow import Schema, fields


class AnswerSchema(Schema):
    id = fields.Int(required=False)
    answer = fields.Str(required=True)
    question_id = fields.Int(required=True)


class AnswersListSchema(Schema):
    answers = fields.Nested(AnswerSchema, many=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    question = fields.Str(required=True)


class QuestionsListSchema(Schema):
    questiona = fields.Nested(QuestionSchema, many=True)


class QuestionAnswerSchema(Schema):
    id = fields.Int(required=False)
    question = fields.Str(required=True)
    answers = fields.Nested(AnswerSchema, many=True)


class QuestionIdSchema(Schema):
    q_id = fields.Int(required=False)
