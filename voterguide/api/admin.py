from import_export import resources
from .models import Candidate


class CandidateResource(resources.ModelResource):
    class Meta:
        model = Candidate
        skip_unchanged = True
        report_skipped = True
        # TODO?
        # exclude created, last_updated fields?
        # that would be on export only, which may not be helpful

    # https://django-import-export.readthedocs.io/en/latest/getting_started.html#advanced-data-manipulation-on-export
    # def dehydrate_running_for_seat(self, candidate):
    #     book_name = getattr(candidate, "name", "unknown")
    #     author_name = getattr(candidate.author, "name", "unknown")
    #     return '%s by %s' % (candidate_name, author_name)


# NOTE: This resource would need to be registered in order to
# manage imports and exports in the admin interface:
# admin.site.register(Candidate, CandidateResource)
