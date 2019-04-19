function UrlGenerator(root) {
    this.root = root;
    this.leagues = [];

    this.toggle = function (id) {
        if (this.leagues.indexOf(id) !== -1)
            this.leagues.splice(this.leagues.indexOf(id), 1);
        else
            this.leagues.push(id);
    };

    this.display_text = function () {
        if (this.leagues.length === 0)
            return "Add some teams!!";

        let leagues = [];

        for (let i = 0; i < this.leagues.length; i++) {
            let elem = document.getElementById(this.leagues[i]);
            let league_name = elem.children.item(1).innerHTML;
            leagues.push(league_name);
        }
        return leagues.join(", ");
    };

    this.url = function () {
        if (this.leagues.length === 0)
            return "#";

        return `${this.root}?leagues=${this.leagues.join(",")}`;
    }
}

function toggle_class(element, cls) {
    if (element.classList.contains(cls))
        element.classList.remove(cls);
    else
        element.classList.add(cls);
}


function main() {
    let url_gen = new UrlGenerator(window.location.toString() + "api/query_leagues");

    let league_buttons = document.getElementsByClassName("league-button");

    let url_element = document.getElementById("calendar_url");
    url_element.innerText = url_gen.display_text();

    for (let i = 0; i < league_buttons.length; i++) {
        league_buttons[i].onclick = function () {
            url_gen.toggle(league_buttons[i].id);
            toggle_class(league_buttons[i], "clicked");
            url_element.innerText = url_gen.display_text();
            url_element.href = url_gen.url()
        }
    }

}

window.addEventListener("DOMContentLoaded", main);
