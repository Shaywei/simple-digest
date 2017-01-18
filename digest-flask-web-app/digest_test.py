# -*- coding: utf-8 -*-
# Copyright (c) 2017 Spotify AB

import os
import json

import unittest
import tempfile

from digest import DigestWebService


class DigestWebServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        os.remove(self.tmp.name)
        self.test_me = DigestWebService(self.tmp.name)
        self.test_me.app.testing = True
        self.client = self.test_me.app.test_client()

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

    def test_empty_db_from_an_empty_file(self):
        self.assertEqual(dict(), self.test_me._load_db())

    def test_no_file(self):
        # Arrange
        tmp = tempfile.NamedTemporaryFile(delete=False)
        os.remove(tmp.name)

        # Act
        test_me = DigestWebService(tmp.name)

        # Assert
        self.assertEqual(dict(), test_me._load_db())

    def test_sha256(self):
        # Arrange
        expected = {"message" :"2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"}  # NOQA

        # Act
        response = self.client.post(
            '/messages',
            headers={'content-type': 'application/json'},
            data=json.dumps({'message': 'foo'}))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEquals(expected, json.loads(response.data))

    def test_put_and_get_one_element(self):
        # Arrange
        self.client.post(
            '/messages',
            headers={'content-type': 'application/json'},
            data=json.dumps({'message': 'foo'}))
        expected = {"message": "foo"}

        # Act
        response = self.client.get('/messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae')  # NOQA

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEquals(expected, json.loads(response.data))

    def test_put_and_get_one_element_persistently(self):
        # Arrange
        self.client.post(
            '/messages',
            headers={'content-type': 'application/json'},
            data=json.dumps({'message': 'foo'}))

        new_service_instance = DigestWebService(self.tmp.name)
        new_service_instance.app.testing = True
        new_client = new_service_instance.app.test_client()

        expected = {"message": "foo"}

        # Act
        response = new_client.get('/messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae')  # NOQA

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEquals(expected, json.loads(response.data))

    def test_non_existing_message(self):
        # Act
        response = self.client.get('/messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae')  # NOQA

        # Assert
        self.assertEqual(404, response.status_code)

    def test_set_invalid_path(self):
        with self.assertRaises(TypeError):
            DigestWebService(None)
