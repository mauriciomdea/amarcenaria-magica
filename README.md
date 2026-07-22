# A Marcenaria Mágica

Site institucional e portfólio da A Marcenaria Mágica, construído com Jekyll e Bootstrap para publicação no GitHub Pages.

## Desenvolvimento local

Requisitos: Ruby compatível com o GitHub Pages e Bundler.

```bash
bundle install
bundle exec jekyll serve --livereload
```

O site ficará disponível em `http://127.0.0.1:4000`.

## Atualização de mídia

Os arquivos originais permanecem fora do repositório. O script abaixo gera AVIF, WebP e JPEG responsivos, remove metadados e atualiza `_data/media.json`:

```bash
python scripts/process_media.py
```

Os HEIC reservados não fazem parte da seleção publicada.

## Configuração antes da publicação

- Ativar `contato@amarcenariamagica.com.br`.
- Informar o ID do GA4 em `_data/site.yml` quando a propriedade existir.
- Cadastrar URLs de marketplaces apenas quando estiverem públicas.
- Confirmar a identificação jurídica na política de privacidade.
- Configurar o domínio no Registro.br e habilitar HTTPS no GitHub Pages.

