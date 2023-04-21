from django.shortcuts import render
from django import forms
from . import util
from django.urls import reverse
import random
import markdown2
from difflib import get_close_matches

# Define a latest page to pass between the selected page and the edit function
latestPage = ""

# Define django forms that will be used in the search bar.
# I have defined different form classesfor search, and for the input when creating a new page


class NewSearchForm(forms.Form):
    search = forms.CharField(
        label="Search Encyclopedia", widget=forms.TextInput)


class TitleForm(forms.Form):
    titleform = forms.CharField(label="Title")


class ContentForm(forms.Form):
    contentform = forms.CharField(label="Content", widget=forms.Textarea)


# This loads a page which displays a list of all the different pages.
# It is linked to via the home button on the layout.html page
# It also includes the form for the search element
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search": NewSearchForm()
    })

# This is what is called when visiting a page content.
# if the page does not exist then an eror page is loaded.
# If the page is found then the content is rendered via title.html
# which shows the title, content and I have also included the serarch form


def get_page(request, title):
    page = util.get_entry(title)
    if page is None:
        return render(request, "encyclopedia/error.html", {
            "error": "404 - page not found. No entry with this title exists on wiki. Please clcick create new page to add one."
        })
    global latestPage
    latestPage = title
    return render(request, "encyclopedia/title.html", {
        'content': markdown2.markdown(page),
        'title': title,
        "search": NewSearchForm()
    })

# This is submitted when the user clicks create new page.
# If submitted via get then it generates the forms required to be submitted
# If submitted via post then it first checks that the user has not tried to
# create a page with a pre-existing title and shows an error page if it has
# Otherwise it will save the new page and render the content page for the newly created page


def new_page(request):
    if request.method == "POST":

        title = TitleForm(request.POST)
        content = ContentForm(request.POST)

        if title.is_valid() and content.is_valid():
            cleantitle = title.cleaned_data["titleform"]
            cleancontent = content.cleaned_data["contentform"]
            titlelist = util.list_entries()
            lowertitlelist = []
            for x in titlelist:
                lowertitlelist.append(x.lower())

            if cleantitle.lower() in lowertitlelist:
                return render(request, "encyclopedia/error.html", {
                    "error": "422 Unprocessable Entity - This title already exists"
                })

            util.save_entry(cleantitle, cleancontent)
            return render(request, "encyclopedia/title.html", {
                'title': cleantitle,
                'content': markdown2.markdown(cleancontent),
                "search": NewSearchForm()
            })

    if request.method == "GET":
        return render(request, "encyclopedia/newpage.html", {
            "formtitle": TitleForm(),
            "formcontent": ContentForm(),
            "search": NewSearchForm()
        })

# Here you edit the existing entries. If request method is get then it
# loads the edit page with a form that contains a text field pre-populated
# with the previouys text.
# When request method is post it updates the content of the page and saves this
# It then renders the updates page


def edit(request):
    latestcontent = util.get_entry(latestPage)

    class PrefilledContentForm(forms.Form):
        contentform = forms.CharField(
            label="Content", widget=forms.Textarea, initial=latestcontent)
    if request.method == "GET":

        return render(request, "encyclopedia/edit.html", {
            "title": latestPage,
            "content": latestcontent,
            "formcontent": PrefilledContentForm(),
            "search": NewSearchForm()
        })

    if request.method == "POST":

        latestcontent = util.get_entry(latestPage)

        newContent = PrefilledContentForm(request.POST)

        if newContent.is_valid():
            cleannewcontent = newContent.cleaned_data["contentform"]
            util.save_entry(latestPage, cleannewcontent)
            return render(request, "encyclopedia/title.html", {
                'title': latestPage,
                'content': markdown2.markdown(cleannewcontent),
                "search": NewSearchForm()
            })

# Simply renders a random page from all the pages


def rand(request):
    titlelist = util.list_entries()
    randomPage = random.choice(titlelist)
    return render(request, "encyclopedia/title.html", {
        'title': randomPage,
        'content': markdown2.markdown(util.get_entry(randomPage)),
        "search": NewSearchForm()
    })

# This was the funcion that was the most complicated
# First I have got the search results from the search input
# If this matched any of the existing pages exactly then I
# have opened that page.
# If it does not match then I have used the function get_close_matches
# to find similar results to the searched text. I have also done this
# while ignoring case
# This then displays a page which has a list of similar matches that
# can be clicked on to open them
# If there are no close matches then "No results found" is displayed


def search(request):

    if request.method == "GET":

        search = NewSearchForm(request.GET)
        entries = util.list_entries()

        if search.is_valid():
            cleanSearch = search.cleaned_data["search"]
            if cleanSearch in entries:
                page = util.get_entry(cleanSearch)
                return render(request, "encyclopedia/title.html", {
                    'content': markdown2.markdown(page),
                    'title': cleanSearch,
                    "search": NewSearchForm()
                })
            else:
                lowercase = []
                for x in entries:
                    lowercase.append(x.lower())
                dict = {lowercase[i]: entries[i] for i in range(len(entries))}
                matcheslowercase = get_close_matches(
                    cleanSearch.lower(), lowercase, cutoff=0.6)
                matchesCaseSensitive = []
                for x in matcheslowercase:
                    matchesCaseSensitive.append(dict[x])
                return render(request, "encyclopedia/search.html", {
                    'search_results': matchesCaseSensitive,
                    "search": NewSearchForm(),
                    "no_results": "No results found",
                })
