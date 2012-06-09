from django.test import TestCase
from news.models import Story
import datetime
from django import forms
from django.forms import ModelForm


class StoryForm(ModelForm):
    class Meta:
        model = Story

thebody = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

# ============

class NewsCreateStory(TestCase):
    def test_new(self):
        story1 = Story.objects.create(
            headline='This is the test headline',
            slug = 'the_test_headline',
            pubdate = datetime.datetime(2011, 04, 10, 0, 37),
            body = thebody,
        )

class MissingFieldsTestCase(TestCase):
    def test_form(self):
        '''Missing required field (slug) on form submit.'''
        post_dict = {'headline': 'Test Title'}
        form = StoryForm(post_dict)
        self.assertFalse(form.is_valid())

class AllRequiredFieldsTestCase(TestCase):
    def test_form(self):
        '''All fields filled out with correct values.'''
        post_dict = {
            'headline': 'Test Title',
            'slug':'test_title',
            'body':thebody,
            'pubdate' : datetime.datetime(2011, 04, 10, 0, 37),
            'modified' : datetime.datetime(2011, 05, 10, 0, 37),            
            } 
        form = StoryForm(post_dict)
        self.assertTrue(form.is_valid())

