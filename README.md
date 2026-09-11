<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/DovletEmin/DovletEmin/main/assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/DovletEmin/DovletEmin/main/assets/header-light.svg">
  <img alt="Dovlet Eminov — Full-Stack Engineer. I build systems that keep running when the network doesn't." src="https://raw.githubusercontent.com/DovletEmin/DovletEmin/main/assets/header-light.svg" width="100%">
</picture>

Most of what I build runs where the cloud is not an option: inside a company network, on one machine, with the internet switched off. That constraint shapes how I work. I care about self-contained deployments, transfers that survive a dropped connection, and services that recover without anyone watching them.

Based in Ashgabat, Turkmenistan. Available for remote work.

---

## This year, woven

<img src="https://raw.githubusercontent.com/DovletEmin/DovletEmin/main/assets/carpet.svg" width="100%" alt="A year of GitHub contributions woven as a Turkmen carpet. Each knot is one day.">

Every knot is one day of commits. The dyes run the traditional Turkmen scale, from thin madder through saffron to undyed wool, and the four levels are recomputed from my own distribution rather than fixed thresholds. A GitHub Action reweaves it from the live calendar every morning.

---

## Selected work

### [Paýlaş](https://github.com/DovletEmin/Paylash_V2) &nbsp;·&nbsp; Go

**Private cloud storage and document collaboration for an architecture studio, running entirely on their own network.**

- Ships as a single Go binary with the frontend embedded. The full stack comes up on a LAN through Docker Compose, with no outbound internet.
- Resumable uploads past 100 GB, presigned multipart straight to object storage. A dropped connection or a page reload does not restart the transfer.
- Real-time co-editing of office documents through Collabora Online over the WOPI protocol.
- Personal, shared and per-project spaces with access control, file versioning, recoverable trash, and an audit log.
- Real-time chat alongside it: presence, typing indicators, read receipts, message search.

<img src="https://raw.githubusercontent.com/DovletEmin/DovletEmin/main/assets/upload-path.svg" width="100%" alt="How a 100 GB upload moves through Paylas: the browser asks the Go binary to start it, the binary records it in Postgres and opens a presigned multipart upload in MinIO, then the browser sends the parts straight to MinIO and resumes from the last completed part after a dropped connection.">

`Go` &nbsp;`PostgreSQL` &nbsp;`MinIO` &nbsp;`Collabora Online` &nbsp;`Caddy` &nbsp;`Docker`

### Digital Information System &nbsp;·&nbsp; [monolith](https://github.com/DovletEmin/Digital-Information-System) &nbsp;/&nbsp; [microservices](https://github.com/DovletEmin/Digital-Information-System-Microservices)

**A university digital library, built twice: once as a single application, once as six services. Same domain, two architectures.**

- The distributed version splits into API gateway, auth, content, search, media and user activity, each with its own datastore.
- Services talk over HTTP for reads and a message broker for everything asynchronous. Search runs on its own index rather than against the primary database.
- Building both taught me the real cost of the split, which is the part most architecture discussions skip.

`Go (Gin)` &nbsp;`Python (FastAPI)` &nbsp;`Node.js` &nbsp;`Next.js` &nbsp;`PostgreSQL` &nbsp;`MongoDB` &nbsp;`Elasticsearch` &nbsp;`RabbitMQ` &nbsp;`MinIO`

### [Presence Service](https://github.com/DovletEmin/Presence-Service) &nbsp;·&nbsp; Python &nbsp;/&nbsp; [Go port](https://github.com/DovletEmin/Presence-Service-GO)

**Real-time presence tracking for chat platforms. Who is online, on which device, and doing what.**

- WebSocket connections with heartbeat monitoring, so a client that dies silently is detected rather than left hanging.
- One user, many concurrent sessions across web, mobile and desktop, aggregated into a single presence state.
- Fan-out through Redis pub/sub, so the service scales horizontally instead of holding every subscriber in one process.
- Also written a second time in Go, against the same design, to put the two concurrency models side by side.

`FastAPI` &nbsp;`WebSocket` &nbsp;`Redis` &nbsp;`Go`

### [Face ID](https://github.com/DovletEmin/Face-ID_Microservice) &nbsp;·&nbsp; Python

**Face recognition on a depth camera, with spoofing protection that a photograph cannot get past.**

- Built on an Intel RealSense D415, using the depth stream to confirm it is looking at a face and not a flat image of one.
- Split into a FastAPI gateway and a recognition service, with a React front end talking over HTTP and WebSocket.

`Python` &nbsp;`FastAPI` &nbsp;`OpenCV` &nbsp;`Intel RealSense` &nbsp;`React` &nbsp;`TypeScript`

### [MirasCloud v2](https://github.com/DovletEmin/MirasCloud-v2) &nbsp;·&nbsp; Go

**File storage for a local network, with a web interface, permissions and an operation history.** Written in Go against MySQL, designed to be deployed once and left alone.

`Go` &nbsp;`MySQL` &nbsp;`Docker`

**Also in these repos:** a real-estate platform on FastAPI, a developer tools API with four independent services, an e-commerce backend built on clean architecture, a trilingual IT terminology API, and a real-time remote log viewer.

---

## Stack

| Layer | What I use |
|:--|:--|
| **Languages** | Go &nbsp;·&nbsp; Python &nbsp;·&nbsp; TypeScript &nbsp;·&nbsp; JavaScript &nbsp;·&nbsp; C# |
| **Backend** | FastAPI &nbsp;·&nbsp; Gin &nbsp;·&nbsp; Express &nbsp;·&nbsp; Django REST Framework |
| **Frontend** | Next.js &nbsp;·&nbsp; React &nbsp;·&nbsp; TypeScript |
| **Data** | PostgreSQL &nbsp;·&nbsp; MongoDB &nbsp;·&nbsp; Redis &nbsp;·&nbsp; Elasticsearch &nbsp;·&nbsp; MySQL |
| **Infrastructure** | Docker &nbsp;·&nbsp; MinIO / S3 &nbsp;·&nbsp; RabbitMQ &nbsp;·&nbsp; Caddy &nbsp;·&nbsp; Linux |
| **Operations** | Prometheus &nbsp;·&nbsp; Grafana &nbsp;·&nbsp; structured logging &nbsp;·&nbsp; health checks |

---

## What I'm good at

**Systems that survive their environment.** Offline-first and LAN-only deployments, self-contained binaries, resumable transfer, graceful recovery. This is the thread running through almost everything above.

**Real-time infrastructure.** WebSocket connection handling at scale, heartbeats and timeout detection, pub/sub fan-out, multi-session state. I have written this service in both Python and Go, so I can talk about the two concurrency models from having used them.

**Deciding when to split a service, and when not to.** I have built the same product both ways, as one application and as six services. I can argue either side with specifics rather than with slogans.

---

## Contact

[![Email](https://img.shields.io/badge/Email-C9452E?style=for-the-badge&logo=maildotru&logoColor=EAE3D9&labelColor=C9452E)](mailto:dovlet.eminov26.02@gmail.com) [![Telegram](https://img.shields.io/badge/Telegram-C9452E?style=for-the-badge&logo=telegram&logoColor=EAE3D9&labelColor=C9452E)](https://t.me/ImEminn) [![LinkedIn](https://img.shields.io/badge/LinkedIn-C9452E?style=for-the-badge&logo=linkedin&logoColor=EAE3D9&labelColor=C9452E)](https://linkedin.com/in/dovlet-eminov) [![Portfolio](https://img.shields.io/badge/Portfolio-C9452E?style=for-the-badge&logo=vercel&logoColor=EAE3D9&labelColor=C9452E)](https://dovlet-eminov.vercel.app)

Open to remote backend and full-stack roles. The fastest way to reach me is Telegram.
