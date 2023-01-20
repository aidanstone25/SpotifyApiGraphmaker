function delete_album(albumID) {
    fetch("/delete_album", {
      method: "POST",
      body: JSON.stringify({ albumID: albumID }),
    }).then((_res) => {
      window.location.href = "/album_rating";
    });
  }