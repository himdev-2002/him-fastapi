# Conventional Commits v1.0.0 Summary

Conventional Commits adalah spesifikasi penulisan pesan commit yang terstruktur dan mudah diproses oleh manusia maupun mesin. Spesifikasi ini memudahkan pembuatan changelog otomatis, penentuan versi (SemVer), dan komunikasi perubahan ke tim.

## Format Pesan Commit

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Elemen utama:**
- `type`: Jenis perubahan (misal: `feat`, `fix`, dll)
- `scope` _(opsional)_: Area/fitur yang terpengaruh
- `description`: Ringkasan singkat perubahan
- `body` _(opsional)_: Penjelasan detail
- `footer` _(opsional)_: Informasi tambahan, seperti BREAKING CHANGE

## Jenis Commit Utama
- **fix:** Memperbaiki bug (patch release)
- **feat:** Menambah fitur baru (minor release)
- **BREAKING CHANGE:** Perubahan mayor, bisa ditulis di footer atau dengan tanda `!` setelah type/scope
- **Lainnya:** `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`, dll

## Contoh Pesan Commit

**Fitur baru:**
```
feat: add user login endpoint
```

**Perbaikan bug:**
```
fix: correct user email validation
```

**Fitur dengan scope:**
```
feat(auth): support OAuth2 login
```

**Perubahan besar (breaking change):**
```
feat!: require email verification for all users
```
atau
```
feat(auth)!: require email verification for all users
```
atau
```
feat: require email verification for all users

BREAKING CHANGE: All users must verify email before login.
```

**Commit dengan body dan footer:**
```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Reviewed-by: Z
Refs: #123
```

**Revert commit:**
```
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

## Manfaat Conventional Commits
- Otomatisasi changelog
- Penentuan versi otomatis (SemVer)
- Komunikasi perubahan lebih jelas
- Memudahkan kontribusi dan review

Referensi: [conventionalcommits.org v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
