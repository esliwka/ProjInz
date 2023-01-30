# from django.test import TestCase
# from .models import Polls, PollRespondents, ClosedQuestions, OpenQuestions, TokenPolls, ClosedAnswers, OpenAnswers, UserPollStatus
# from django.contrib.auth import get_user_model

# class PollsModelTests(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         User = get_user_model()
#         user = User.objects.create(email='test@example.com', first_name='John', last_name='Doe')
#         Polls.objects.create(poll_owner_id=user, poll_name='Test Poll', poll_text='This is a test poll')

#     def test_poll_name_label(self):
#         poll = Polls.objects.get(id=1)
#         field_label = poll._meta.get_field('poll_name').verbose_name
#         self.assertEqual(field_label, 'poll name')

#     def test_poll_text_label(self):
#         poll = Polls.objects.get(id=1)
#         field_label = poll._meta.get_field('poll_text').verbose_name
#         self.assertEqual(field_label, 'poll text')

#     def test_poll_owner_label(self):
#         poll = Polls.objects.get(id=1)
#         field_label = poll._meta.get_field('poll_owner_id').verbose_name
#         self.assertEqual(field_label, 'poll owner')

#     def test_poll_name_max_length(self):
#         poll = Polls.objects.get(id=1)
#         max_length = poll._meta.get_field('poll_name').max_length
#         self.assertEqual(max_length, 255)

#     def test_poll_owner_is_CustomUser_instance(self):
#         poll = Polls.objects.get(id=1)
#         poll_owner = poll.poll_owner_id
#         self.assertTrue(isinstance(poll_owner, get_user_model()))

#     def test_string_representation(self):
#         poll = Polls.objects.get(id=1)
#         self.assertEqual(str(poll), poll.poll_name)

#     def test_poll_summary(self):
#         poll = Polls.objects.get(id=1)
#         self.assertEqual(poll.poll_summary(), 'This is a test poll')

#     def test_poll_owner_name(self):
#         poll = Polls.objects.get(id=1)
#         self.assertEqual(poll.poll_owner_name(), 'John Doe')

# class ClosedQuestionsModelTests(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         User = get_user_model()
#         user = User.objects.create(email='test@example.com', first_name='John', last_name='Doe')
#         poll = Polls.objects.create(poll_owner_id=user, poll_name='Test Poll', poll_text='This is a test poll')
#         ClosedQuestions.objects.create(poll_id=poll, question_text='What is your favorite color?')

#     def test_question_text_label(self):
#         closed_question = ClosedQuestions.objects.get(id=1)
#         field_label = closed_question._meta.get_field('question_text').verbose_name
#         self.assertEqual(field_label, 'question text')

#     def test_poll_id_label(self):
#         closed_question = ClosedQuestions.objects.get(id=1)
#         field_label = closed_question._meta.get_field('poll_id').verbose_name
#         self.assertEqual(field_label, 'poll')

#     def test_poll_id_is_Poll_instance(self):
#         closed_question = ClosedQuestions.objects.get(id=1)
#         poll = closed_question.poll_id
#         self.assertTrue(isinstance(poll, Polls))
