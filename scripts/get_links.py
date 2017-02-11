from goose import Goose

goose = Goose()

landing_url = 'http://zizek.uk/democracy-versus-the-people/'
article = goose.extract(landing_url)

# clean up links
links = [link for link in a.links
		 	if '?share=' not in link
		 	and not link.endswith('.pdf')
		 	and not link.startswith('whatsapp://')]

links = [link for link in a.links if url not in link]
pages = [link for link in a.links if url in link and link.endswith('/')]