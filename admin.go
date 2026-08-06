package main

import (
	"embed"
	"encoding/json"
	"net/http"
	"os"
)

//go:embed admin.html
var adminHTML embed.FS

func getAdminToken() string {
	token := os.Getenv("ADMIN_TOKEN")
	if token == "" {
		token = "supersecret123"
	}
	return token
}

func adminOnly(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		token := r.URL.Query().Get("token")
		if token != getAdminToken() {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}
		next(w, r)
	}
}

func adminPageHandler(w http.ResponseWriter, r *http.Request) {
	content, err := adminHTML.ReadFile("admin.html")
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Write(content)
}

func listChannels(w http.ResponseWriter, r *http.Request) {
	channelStore.RLock()
	defer channelStore.RUnlock()
	list := make([]Channel, 0, len(channelStore.items))
	for _, ch := range channelStore.items {
		list = append(list, ch)
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(list)
}

func addChannel(w http.ResponseWriter, r *http.Request) {
	var ch Channel
	if err := json.NewDecoder(r.Body).Decode(&ch); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	if ch.Slug == "" || ch.URL == "" {
		http.Error(w, "Slug and URL are required", http.StatusBadRequest)
		return
	}
	channelStore.Lock()
	defer channelStore.Unlock()
	channelStore.items[ch.Slug] = ch
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(ch)
}

func deleteChannel(w http.ResponseWriter, r *http.Request) {
	slug := r.URL.Path[len("/admin/channels/delete/"):]
	if slug == "" {
		http.Error(w, "Slug required", http.StatusBadRequest)
		return
	}
	channelStore.Lock()
	defer channelStore.Unlock()
	if _, ok := channelStore.items[slug]; !ok {
		http.NotFound(w, r)
		return
	}
	delete(channelStore.items, slug)
	w.WriteHeader(http.StatusNoContent)
}
