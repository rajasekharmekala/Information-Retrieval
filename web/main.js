let searchButton = document.getElementById("searchbarbutton")
let searchField = document.getElementById("searchbartext")
let searchResults = document.getElementById("searchresultsarea")
let searchTimeText = document.getElementById("searchtimetext")

let searchClicked = (event)=>{
    let text = searchField.value
    if(!text){
        updateResults([], "")
        alert("Please enter a valid text!")
    }else{
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
               // Typical action to be performed when the document is ready:
                data = JSON.parse(xhttp.responseText);
                result = data.result
                updateResults(result, data.time || "")
            }
        };
        xhttp.open("GET", "/query/"+text, true);
        xhttp.send();
    }
}




let updateResults = (result, time)=>{
    result = result || []


//     <div class="searchresult">
//     <h2>Lock (computer science) - Wikipedia</h2>
//     <a>https://en.wikipedia.org/wiki/Lock_(computer_science)</a> <button>▼</button>
//     <p>In computer science, a lock or mutex (from mutual exclusion) is a synchronization mechanism for enforcing limits on access to a resource in an</p>
//     <p> environment where there are many threads of execution.</p>
// </div>

    while (searchResults.firstChild) {
        searchResults.removeChild(searchResults.firstChild);
    }

    if(result.length == 0){
        let p = document.createElement('p');
        p.appendChild(document.createTextNode("No results found"))

        searchResults.appendChild(p)
        return
    }


    for (let i = 0; i < result.length; i++) {
        let item = document.createElement('div');
        item.classList.add("searchresult")
        let h2 = document.createElement('h2');
        let a = document.createElement('a');
        let p = document.createElement('p');
        h2.appendChild(document.createTextNode(result[i].title || result[i].url ));
        a.appendChild(document.createTextNode(result[i].url))
        p.appendChild(document.createTextNode(result[i].display_text))
        item.appendChild(h2)
        item.appendChild(a)
        item.appendChild(p)
        item.addEventListener('click', ()=> window.location=result[i].url)
        searchResults.appendChild(item);
    }

    while (searchTimeText.firstChild) {
        searchTimeText.removeChild(searchTimeText.firstChild)
    }
    let p_t = document.createElement('p');
    p_t.appendChild(document.createTextNode(time))
    searchTimeText.appendChild(p_t)


}

if(searchButton && searchResults && searchField && searchTimeText){
    searchButton.addEventListener('click', searchClicked)
    searchField.addEventListener('keydown', (event)=>{
    if(event.keyCode == 13){
        searchClicked(event)
    }
    })
}

