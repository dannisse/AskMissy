function deleteNote(noteId){
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId})
    }).then((_res) => {
        window.location.href = " ";
    });
}

function openForm() {
  document.getElementById("myForm").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
}

function handleLinkClick() {
    let index = $(this).attr("id");
}

function displayClass() {
    document
}