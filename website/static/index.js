function deleteAlbum(albumID) {
    fetch("/deleteAlbum", {
      method: "POST",
      body: JSON.stringify({ albumID: albumID }),
    }).then((_res) => {
      window.location.href = "/delete_album";
    });
  }