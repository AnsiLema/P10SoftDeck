from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Project, Contributor

User = get_user_model()


class ProjectPermissionsTest(APITestCase):
    """ Tests IsContributor & IsAuthor permissions """

    def setUp(self):
        """ Prepares data for the test by creating users and projects"""
        self.author = User.objects.create_user(username="author", password="Test@1234")
        self.contributor = User.objects.create_user(username="contributor", password="Test@1234")
        self.other_user = User.objects.create_user(username="other_user", password="Test@1234")

        self.project = Project.objects.create(title="Test Project Bis", description="Desc", type="BACKEND",
                                              author=self.author)
        Contributor.objects.create(user=self.contributor, project=self.project)

        self.author_token = self.get_token("author", "Test@1234")
        self.contributor_token = self.get_token("contributor", "Test@1234")
        self.other_user_token = self.get_token("other_user", "Test@1234")

    def get_token(self, username, password):
        """ Get token for a user"""
        response = self.client.post("/api/login/",
                                    {"username": username, "password": password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, "The token retrieval failed")
        return response.data.get("access")

    def test_contributor_can_access_project(self):
        """ Un contributeur peut voir un projet """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.contributor_token}')
        response = self.client.get(f"/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_contributor_cannot_access_project(self):
        """ Un utilisateur non-contributeur ne peut pas voir un projet """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_user_token}')
        response = self.client.get(f"/api/projects/{self.project.id}/")
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            self.fail("Authentication failed. Ensure that the 'other_user' token is valid.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_project(self):
        """ L'auteur peut supprimer son projet """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.author_token}')

        # 🔹 Vérifie que le projet existe avant la suppression
        print("Avant suppression :", Project.objects.all())

        response = self.client.delete(f"/api/projects/{self.project.id}/")

        # 🔹 Vérifie ce qui est retourné en cas d'échec
        print("Réponse suppression :", response.status_code, response.data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 🔹 Vérifie que le projet a bien été supprimé
        print("Après suppression :", Project.objects.all())

    def test_non_author_cannot_delete_project(self):
        """ Un non-auteur ne peut pas supprimer un projet """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.contributor_token}')
        response = self.client.delete(f"/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
