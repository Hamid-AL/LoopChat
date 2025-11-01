# LoopChat

A real-time chat application using Django, Django Channels, WebSockets, and Redis.

Features:
- Real-time messaging in chat rooms
- Private one-on-one messaging
- Friend management system
- Online status indicators

# 🧩 Architecture Overview
``` mermaid
    %%{init: {'theme':'base', 'themeVariables': { 
        'primaryColor': '#2563eb',          /* Bright blue */
        'primaryTextColor': '#ffffff', 
        'primaryBorderColor': '#1e40af', 
        'lineColor': '#10b981',             /* Green lines */
        'secondaryColor': '#fbbf24',        /* Vibrant yellow */
        'tertiaryColor': '#9333ea',         /* Purple accent */
        'edgeLabelBackground':'#f1f5f9',    /* Light background for edge labels */
        'background':'#ffffff'              /* White background for clarity */
    }}}%%
    flowchart TB
        subgraph Client["🌐 Client Layer - Frontend"]
            direction TB
            Browser[Browser Client]
            Templates[HTML Templates]
            Static[Static Files<br/>CSS/JS]
            
            Browser --> Templates
            Browser --> Static
        end
        
        subgraph Server["⚙️ Server Layer - Django Backend"]
            direction TB
            
            ASGI[ASGI Application<br/>Handles HTTP & WebSocket]
            
            subgraph Routing["📡 Routing Layer"]
                URLRouter[HTTP URL Router<br/>server/urls.py]
                WSRouter[WebSocket Router<br/>chat/routing.py]
            end
            
            subgraph MiddlewareLayer["🛡️ Middleware Stack"]
                Middleware[Security, Auth, CSRF<br/>Session Management]
            end
            
            subgraph UsersApp["👥 Users Application"]
                direction LR
                UsersURLs[URLs:<br/>/users/login/<br/>/users/signup/<br/>/users/logout/<br/>/users/friend-request/*]
                UsersViews[Views:<br/>Authentication<br/>Friend Management]
                UsersModels[Models:<br/>Profile<br/>Friendship<br/>FriendRequest]
                
                UsersURLs --> UsersViews
                UsersViews --> UsersModels
            end
            
            subgraph ChatApp["💬 Chat Application"]
                direction LR
                ChatURLs[URLs:<br/>/chat/<br/>/chat/room/*<br/>/chat/user/*<br/>/chat/friends/]
                ChatViews[Views:<br/>Room Management<br/>Chat Interface]
                ChatModels[Models:<br/>ChatRoom<br/>RoomMessage<br/>DirectMessage]
                ChatConsumers[WebSocket Consumers:<br/>ChatRoomConsumer<br/>PrivateMessageConsumer<br/>NotificationConsumer]
                
                ChatURLs --> ChatViews
                ChatViews --> ChatModels
                ChatConsumers --> ChatModels
            end
            
            ASGI --> MiddlewareLayer
            MiddlewareLayer --> URLRouter
            MiddlewareLayer --> WSRouter
            URLRouter --> UsersApp
            URLRouter --> ChatApp
            WSRouter --> ChatConsumers
        end
        
        subgraph Infrastructure["🔧 Infrastructure Layer"]
            direction TB
            Redis[(Redis Channel Layer<br/>Message Broker<br/>Port: 6379)]
            DB[(SQLite Database<br/>db.sqlite3<br/>Data Persistence)]
            Docker[Docker Container<br/>redis:7 + redisinsight]
            
            Redis -.-> Docker
        end
        
        %% Client to Server connections
        Browser -->|HTTP Requests| ASGI
        Browser -->|WebSocket Connections| ASGI
        
        %% Consumers to Redis
        ChatConsumers <-->|Real-time Messaging| Redis
        ChatConsumers -->|Broadcast Messages| Redis
        Redis -->|Receive Messages| ChatConsumers
        
        %% Models to Database
        UsersModels <-->|ORM Queries| DB
        ChatModels <-->|ORM Queries| DB
        ChatConsumers -->|Save Messages| DB
        ChatViews -->|Load Messages| DB
        
        %% Styling
        classDef clientStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
        classDef serverStyle fill:#fff4e1,stroke:#e65100,stroke-width:2px,color:#000
        classDef usersStyle fill:#ffe1f5,stroke:#880e4f,stroke-width:2px,color:#000
        classDef chatStyle fill:#e1ffe1,stroke:#1b5e20,stroke-width:2px,color:#000
        classDef infraStyle fill:#f0e1ff,stroke:#4a148c,stroke-width:2px,color:#000
        classDef middlewareStyle fill:#fff5e1,stroke:#e65100,stroke-width:2px,color:#000
        
        class Browser,Templates,Static clientStyle
        class ASGI,URLRouter,WSRouter serverStyle
        class UsersURLs,UsersViews,UsersModels usersStyle
        class ChatURLs,ChatViews,ChatModels,ChatConsumers chatStyle
        class Redis,DB,Docker infraStyle
        class Middleware middlewareStyle
```

## 🖥️ Client Layer
- **Browser:** Renders HTML templates and executes JavaScript.  
- **Templates:** Django HTML templates for UI (login, chat, friends).  
- **Static files:** CSS and JavaScript for styling and interactivity.  

---

## ⚙️ Server Layer

### ASGI Application
- Entry point handling both **HTTP** and **WebSocket** connections.

### Routing Layer
- **HTTP URL Router:** Routes HTTP requests to views.  
- **WebSocket Router:** Routes WebSocket connections to consumers.  

### Middleware Stack
- Security, authentication, CSRF protection, session management.

---

### 👥 Users App
- **Authentication:** Login, signup, logout.  
- **Friend management:** Send, accept, or reject friend requests; remove friends.  
- **Models:**  
  - `Profile`  
  - `Friendship`  
  - `FriendRequest`

---

### 💬 Chat App
- **Room management:** Create, delete, and list chat rooms.  
- **Chat interface:** Handles room and private messages.  
- **WebSocket consumers:** Manage real-time communication.  
- **Models:**  
  - `ChatRoom`  
  - `RoomMessage`  
  - `DirectMessage`

---

## 🏗️ Infrastructure Layer
- **Redis Channel Layer:**  
  - Message broker for WebSocket communication.  
  - Broadcasts messages to connected clients.  
  - Manages channel groups (rooms, private chats, notifications).  
- **SQLite Database:**  
  - Persistent storage for user data, profiles, friendships, rooms, and messages.  
- **Docker:**  
  - Containerized Redis service for local development.

---

## 🔁 Data Flow

### HTTP Requests
`Browser → ASGI → URL Router → Views → Models → Database`

### WebSocket Connections
`Browser ↔ ASGI ↔ WebSocket Router ↔ Consumers ↔ Redis`

### Real-Time Messaging
`Consumer receives message → Saves to DB → Broadcasts via Redis → Other clients receive`
 

## 📘 Get started
- To run the app localy visit:[get_started](docs/get_started.md) 
- To learn more about different workflows visit: [diagrames](docs/diagrams.md) 
