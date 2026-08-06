package main

import (
	"fmt"
	"log"
	"net/http"
)

func LiveHandler(w http.ResponseWriter, r *http.Request) {
	slug := r.URL.Path[len("/live/"):]

	// channelStore'dan oku
	channelStore.RLock()
	ch, ok := channelStore.items[slug]
	channelStore.RUnlock()
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
		log.Printf("ResolveYoutube error for %s: %v", slug, err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	SetCache(slug, url)
	http.Redirect(w, r, url, http.StatusFound)
}

func PlaylistHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "audio/x-mpegurl")
	w.Header().Set("Content-Disposition", "inline; filename=playlist.m3u")

	fmt.Fprintln(w, "#EXTM3U")

	// Dinamik host adresi
	scheme := "http"
	if r.TLS != nil {
		scheme = "https"
	}
	host := r.Host // örn: yt.tecostream.xyz:8050

	channelStore.RLock()
	defer channelStore.RUnlock()

	for slug, ch := range channelStore.items {
		fmt.Fprintf(w,
			"#EXTINF:-1 tvg-id=\"%s\" tvg-name=\"%s\" group-title=\"%s\",%s\n",
			slug,
			ch.Name,
			ch.Group,
			ch.Name,
		)
		fmt.Fprintf(w,
			"%s://%s/live/%s\n\n",
			scheme,
			host,
			slug,
		)
	}
}

func main() {
	http.HandleFunc("/live/", LiveHandler)
	http.HandleFunc("/playlist.m3u", PlaylistHandler)

	// Admin API'leri
	http.HandleFunc("/admin/channels", adminOnly(listChannels))
	http.HandleFunc("/admin/channels/add", adminOnly(addChannel))
	http.HandleFunc("/admin/channels/delete/", adminOnly(deleteChannel))

	// Admin web arayüzü
	http.HandleFunc("/admin", adminOnly(adminPageHandler))

	log.Printf("Server started on %s", ListenAddr)
	log.Fatal(http.ListenAndServe(ListenAddr, nil))
}
