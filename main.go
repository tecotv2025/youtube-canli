package main

import (
	"fmt"
	"log"
	"net/http"
)

func LiveHandler(w http.ResponseWriter, r *http.Request) {

	slug := r.URL.Path[len("/live/"):]

	ch, ok := Channels[slug]
	if !ok {
		http.NotFound(w, r)
		return
	}

	if url, ok := GetCache(slug); ok {
		http.Redirect(w, r, url, http.StatusFound)
		return
	}

	url, err := ResolveYoutube(ch)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SetCache(slug, url)

	http.Redirect(w, r, url, http.StatusFound)
}

func PlaylistHandler(w http.ResponseWriter, r *http.Request) {

	w.Header().Set("Content-Type", "audio/x-mpegurl")
	w.Header().Set("Content-Disposition", "inline; filename=playlist.m3u")

	fmt.Fprintln(w, "#EXTM3U")

	for slug, ch := range Channels {

		fmt.Fprintf(w,
			"#EXTINF:-1 tvg-id=\"%s\" tvg-name=\"%s\" group-title=\"YouTube\",%s\n",
			slug,
			ch.Name,
			ch.Name,
		)

		fmt.Fprintf(w,
			"https://yt.tecostream.xyz/live/%s\n\n",
			slug,
		)
	}
}

func main() {

	http.HandleFunc("/live/", LiveHandler)
	http.HandleFunc("/playlist.m3u", PlaylistHandler)

	log.Println("Server başladı :8080")

	log.Fatal(http.ListenAndServe(ListenAddr, nil))
}
