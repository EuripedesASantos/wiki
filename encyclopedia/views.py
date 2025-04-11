import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse

from . import util

import markdown2


class SearchForm(forms.Form):
    searched = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'search'}))

class NewPageForm(forms.Form):
    new_name = forms.CharField()
    markdown_text = forms.CharField()


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def redirect(request):
    return HttpResponseRedirect("wiki/")
def render_page(request, page_name):

    if page_name in util.list_entries():
        return render(request, "encyclopedia/index_wiki.html", {
            "page_name": page_name,
            "mark_content": markdown2.markdown(util.get_entry(page_name)),
            "form": SearchForm()
        })
    else:
        return render(request, "encyclopedia/index_wiki.html", {
            "page_name": page_name,
            "mark_content": "<h1>" + page_name + "</h1><p>The requested page was not found!</p>",
            "form": SearchForm()
        })


def search_in_page(entry_name: str, searched: str, founds: dict):
    page = util.get_entry(entry_name)
    page = page.strip('\r')

    temp_dic = {entry_name: []}
    for ln in page.split('\n'):
        if searched.upper() in ln.upper():
            temp_dic[entry_name].append(ln)

    if len(temp_dic[entry_name]):
        founds[entry_name] = temp_dic[entry_name]

def render_results(founds: dict) -> str:
    html = ''
    for name, values in founds.items():
        html += f'<div><a href="/wiki/{name}"><b>{name}</b>'

        for ln in values:
            html += f'<div>{markdown2.markdown(ln)}</div>'

        html += '</a></div>'

    return html


def search(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = SearchForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            searching = form.cleaned_data["searched"]

            # If the query matches the name of an encyclopedia entry, the user should be redirected
            # to that entry’s page.
            for x in util.list_entries():
                if searching.upper() == x.upper():
                    return render(request, "encyclopedia/index_wiki.html", {
                        "page_name": x,
                        "mark_content": markdown2.markdown(util.get_entry(x)),
                        "form": SearchForm()
                    })

            # If the query does not match the name of an encyclopedia entry, the user should instead
            # be taken to a search results page that displays a list of all encyclopedia entries that
            # have the query as a substring. For example, if the search query were ytho, then Python
            # should appear in the search results.
            founds = {}
            for x in util.list_entries():
                search_in_page(x, searching, founds)

            if founds:
                # Show page's results
                return render(request, "encyclopedia/index_wiki.html", {
                    "page_name": "Search results: ",
                    "mark_content": render_results(founds),
                    "form": SearchForm()
                })
            else:
                # Show page's no results
                return render(request, "encyclopedia/index_wiki.html", {
                    "page_name": "Search results: ",
                    "mark_content": f"<h1>Search results!</h1><p>No results for {searching}!</p>",
                    "form": SearchForm()
                })
    else:
        return HttpResponseRedirect(reverse("wiki:index"))

def new_wiki(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            new_name = form.cleaned_data["new_name"]
            markdown_text = form.cleaned_data["markdown_text"]

            for x in util.list_entries():
                if new_name.upper() == x.upper():
                    return render(request, "encyclopedia/index_new.html", {
                        "page_name": "New wiki page",
                        "action_url": reverse("wiki:new_wiki"),
                        "message": f'The new wiki page exists: <a href="/wiki/{x}">{x}</a>',
                        "new_name": x,
                        "mark_content": markdown_text,
                        "form": SearchForm(),
                        "button_text": "Save new wiki"
                    })

            util.save_entry(new_name, markdown_text)
            return render_page(request, new_name)

    return render(request, "encyclopedia/index_new.html", {
        "page_name": "New wiki page",
        "action_url": reverse("wiki:new_wiki"),
        "message": "Creating a new wiki page!",
        "new_name": "",
        "mark_content": "",
        "form": SearchForm(),
        "button_text": "Save new wiki"
    })

def random_page(request):
    page_name = random.choice(util.list_entries())
    return render_page(request, page_name)

def edit_wiki_list(request):
    return render(request, "encyclopedia/index_edit_list.html", {
        "page_name": "Edit wiki page",
        "message": "Select wiki page to edit",
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def edit_wiki(request, page_name):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            new_name = form.cleaned_data["new_name"]
            markdown_text = form.cleaned_data["markdown_text"]

            for x in util.list_entries():
                if new_name.upper() == x.upper():
                    util.save_entry(x, markdown_text)
                    return render_page(request, x)


            util.save_entry(new_name, markdown_text)
            return render_page(request, new_name)

    if page_name == '':
        # Redirect user to page's edit wiki
        # if the name of wiki page to edit is empty
        return HttpResponseRedirect(reverse("wiki:edit_wiki_list"))
    elif page_name in util.list_entries():
        return render(request, "encyclopedia/index_new.html", {
            "page_name": "Editing wiki page",
            "action_url": f'/wiki/edit/{page_name}',
            "message": f'Editing page: <a href="/wiki/{page_name}">{page_name}</a>',
            "new_name": page_name,
            "mark_content": util.get_entry(page_name).replace('\r', ''),
            "form": SearchForm(),
            "button_text": "Save edit wiki"
        })
    else:
        # Displays the message that the wiki does not exist
        # if the user tries to edit a page that does not exist
        return render(request, "encyclopedia/index_new.html", {
            "page_name": "Wiki does not exists",
            "action_url": reverse("wiki:new_wiki"),
            "message": f"Wiki does not exists: <b>{page_name}</b>, but you can create a new!",
            "new_name": page_name,
            "mark_content": f"# {page_name}",
            "form": SearchForm(),
            "button_text": "Save edit wiki"
        })
