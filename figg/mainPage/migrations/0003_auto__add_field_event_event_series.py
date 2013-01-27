# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Event.event_series'
        db.add_column('mainPage_event', 'event_series',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mainPage.EventSeries'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Event.event_series'
        db.delete_column('mainPage_event', 'event_series_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mainPage.attendingstatus': {
            'Meta': {'object_name': 'AttendingStatus'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attending_status'", 'to': "orm['mainPage.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attending_status'", 'to': "orm['auth.User']"})
        },
        'mainPage.chosenfew': {
            'Meta': {'object_name': 'ChosenFew'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'mainPage.event': {
            'Meta': {'ordering': "['key']", 'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'event_series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.EventSeries']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.EventImage']", 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.BigIntegerField', [], {}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.Venue']", 'null': 'True', 'blank': 'True'})
        },
        'mainPage.eventimage': {
            'Meta': {'object_name': 'EventImage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'mainPage.eventseries': {
            'Meta': {'object_name': 'EventSeries'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'mainPage.invitedstatus': {
            'Meta': {'object_name': 'InvitedStatus'},
            'from_attending_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_invited_status'", 'to': "orm['mainPage.AttendingStatus']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_attending_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_invited_status'", 'to': "orm['mainPage.AttendingStatus']"})
        },
        'mainPage.note': {
            'Meta': {'ordering': "['-updated']", 'object_name': 'Note'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'note_creator'", 'to': "orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mentions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'note_mentions'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'published': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'note_published'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mainPage.revealedcal': {
            'Meta': {'object_name': 'RevealedCal'},
            'cal': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'cal_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_viewed': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'mainPage.selectedcal': {
            'Meta': {'object_name': 'SelectedCal'},
            'cal': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'cal_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_viewed': ('django.db.models.fields.DateTimeField', [], {}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.Tag']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'mainPage.tag': {
            'Meta': {'object_name': 'Tag'},
            'cals': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tag_cals'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags'", 'symmetrical': 'False', 'to': "orm['mainPage.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notes'", 'symmetrical': 'False', 'to': "orm['mainPage.Note']"}),
            'removal_requested': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tag_removal'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'mainPage.venue': {
            'Meta': {'object_name': 'Venue'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        'mainPage.venueowner': {
            'Meta': {'object_name': 'VenueOwner'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.Venue']"})
        },
        'mainPage.viewedcalendar': {
            'Meta': {'object_name': 'ViewedCalendar'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_viewed': ('django.db.models.fields.DateTimeField', [], {}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'viewed': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'viewed_tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainPage.Tag']", 'null': 'True', 'blank': 'True'}),
            'viewer': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['mainPage']