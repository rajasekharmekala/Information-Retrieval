let searchButton = document.getElementById("searchbarbutton")
let searchField = document.getElementById("searchbartext")
let searchResults = document.getElementById("searchresultsarea")

let searchClicked = (event)=>{
    let text = searchField.value
    if(!text){
        updateResults([])
        alert("Please enter a valid text!")
    }else{
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
               // Typical action to be performed when the document is ready:
                data = JSON.parse(xhttp.responseText);
                result = data.result
                updateResults(result)
            }
        };
        xhttp.open("GET", "/query/"+text, true);
        xhttp.send();
    }
}


let updateResults = (array)=>{
    array = array || []

//     <div class="searchresult">
//     <h2>Lock (computer science) - Wikipedia</h2>
//     <a>https://en.wikipedia.org/wiki/Lock_(computer_science)</a> <button>▼</button>
//     <p>In computer science, a lock or mutex (from mutual exclusion) is a synchronization mechanism for enforcing limits on access to a resource in an</p>
//     <p> environment where there are many threads of execution.</p>
// </div>

while (searchResults.firstChild) {
    searchResults.removeChild(searchResults.firstChild);
}

    for (var i = 0; i < array.length; i++) {
        var item = document.createElement('div');
        item.classList.add("searchresult")
        var h2 = document.createElement('h2');
        h2.appendChild(document.createTextNode(array[i]));
        item.appendChild(h2)
        searchResults.appendChild(item);
    }
}

if(searchButton && searchResults && searchField){
    searchButton.addEventListener('click', searchClicked)
}

