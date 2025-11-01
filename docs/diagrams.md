These workflows cover:
- User Authentication: Login, signup, logout
- Friend Management: Sending, accepting, rejecting requests
- Room Chat: Creating rooms, joining, sending messages
- Private Messaging: Friend verification, real-time chat
- WebSocket Flow: Connection establishment and message routing
- Online Status: Real-time presence updates
- Message Flow: End-to-end message sending process
- Use these in your documentation or README to explain how the application works.


## 1. User Authentication Flow

```mermaid
    flowchart TD
    Start([User visits site]) --> CheckAuth{Is User<br/>Authenticated?}
    CheckAuth -->|No| LoginPage[Show Login Page]
    CheckAuth -->|Yes| Dashboard[Show Friends Dashboard]
    
    LoginPage --> UserInput[User enters<br/>username & password]
    UserInput --> Validate[Authenticate User]
    
    Validate -->|Valid| CreateSession[Create Session]
    CreateSession --> RedirectHome[Redirect to<br/>Friends Page]
    RedirectHome --> Dashboard
    
    Validate -->|Invalid| ErrorMsg[Show Error Message]
    ErrorMsg --> LoginPage
    
    LoginPage --> SignupLink[Click Signup Link]
    SignupLink --> SignupPage[Show Signup Page]
    SignupPage --> SignupInput[User enters<br/>username, email, passwords]
    SignupInput --> CheckPassword{Passwords<br/>Match?}
    
    CheckPassword -->|No| SignupError[Show Password Mismatch Error]
    SignupError --> SignupPage
    
    CheckPassword -->|Yes| CheckUsername{Username<br/>Exists?}
    CheckUsername -->|Yes| UsernameError[Show Username Exists Error]
    UsernameError --> SignupPage
    
    CheckUsername -->|No| CreateUser[Create User Account]
    CreateUser --> CreateProfile[Create Profile via Signal]
    CreateProfile --> SuccessMsg[Show Success Message]
    SuccessMsg --> LoginPage
    
    Dashboard --> Logout[User Logs Out]
    Logout --> DestroySession[Destroy Session]
    DestroySession --> LoginPage

```
## 2. Friend Request Workflow

```mermaid
    flowchart TD
    Start([User on Friends Page]) --> ViewUsers[Display All Users<br/>except current user]
    ViewUsers --> UserAction{User Action}
    
    UserAction -->|Click Send Friend Request| CheckSelf{Is Target<br/>Current User?}
    CheckSelf -->|Yes| SelfError[Error: Cannot add self]
    SelfError --> ViewUsers
    
    CheckSelf -->|No| CheckExisting{Request<br/>Exists?}
    CheckExisting -->|Yes - Accepted| AlreadyFriends[Error: Already friends]
    CheckExisting -->|Yes - Pending/Rejected| DeleteOld[Delete Old Request]
    CheckExisting -->|No| CreateRequest[Create FriendRequest<br/>status: pending]
    
    DeleteOld --> CreateRequest
    CreateRequest --> SuccessMsg[Success Message]
    AlreadyFriends --> ViewUsers
    SuccessMsg --> ViewUsers
    
    UserAction -->|See Pending Request| ViewPending[Show Pending Requests]
    ViewPending --> RequestAction{Action on<br/>Request}
    
    RequestAction -->|Accept| AcceptRequest[Accept Friend Request]
    AcceptRequest --> UpdateStatus[Update status: accepted]
    UpdateStatus --> CreateFriendship[Add to Friends<br/>Many-to-Many]
    CreateFriendship --> SuccessAccept[Success: Now friends]
    SuccessAccept --> ViewUsers
    
    RequestAction -->|Reject| RejectRequest[Update status: rejected]
    RejectRequest --> ViewUsers
    
    RequestAction -->|Remove Friend| RemoveFriendship[Remove from Friends]
    RemoveFriendship --> DeleteRequests[Delete FriendRequests]
    DeleteRequests --> ViewUsers

```


## 3. Room Chat Workflow
```mermaid
    flowchart TD
    Start([User accesses Chat]) --> ViewRooms[Display Available Rooms]
    ViewRooms --> UserChoice{User Action}
    
    UserChoice -->|Create New Room| CreateRoom[POST: Create Room]
    CreateRoom --> ValidateRoom{Room Name<br/>Valid?}
    ValidateRoom -->|Invalid/Exists| RoomError[Show Error]
    RoomError --> ViewRooms
    
    ValidateRoom -->|Valid| SaveRoom[Save ChatRoom to DB]
    SaveRoom --> AddCreator[Add Creator as Member]
    AddCreator --> RedirectRoom[Redirect to Room Page]
    
    UserChoice -->|Join Existing Room| SelectRoom[Select Room]
    SelectRoom --> LoadRoom[Load Room Data]
    LoadRoom --> LoadMessages[Load Previous Messages<br/>from Database]
    LoadMessages --> RenderRoom[Render Room Chat Page]
    
    RenderRoom --> EstablishWS[Establish WebSocket<br/>Connection]
    EstablishWS --> AuthCheck{User<br/>Authenticated?}
    AuthCheck -->|No| CloseWS[Close WebSocket]
    AuthCheck -->|Yes| AddToRoom[Add User to Room Members]
    AddToRoom --> JoinGroup[Join Channel Group<br/>via Redis]
    JoinGroup --> WSReady[WebSocket Ready]
    
    WSReady --> UserSends[User Sends Message]
    UserSends --> ReceiveWS[WebSocket Receives Message]
    ReceiveWS --> SaveMessage[Save RoomMessage<br/>to Database]
    SaveMessage --> BroadcastRedis[Broadcast to Redis<br/>Channel Group]
    BroadcastRedis --> RedisDistributes[Redis Distributes<br/>to All Group Members]
    RedisDistributes --> AllClients[All Clients in Room<br/>Receive Message]
    AllClients --> UpdateUI[Update UI for All Users]
    
    UserChoice -->|Delete Room| DeleteRoom[POST: Delete Room]
    DeleteRoom --> RemoveFromDB[Delete from Database]
    RemoveFromDB --> ViewRooms

```


## 4. Private Message Workflow
```mermaid
    flowchart TD
    Start([User wants to chat privately]) --> CheckFriendship{Is Target<br/>a Friend?}
    CheckFriendship -->|No| NotFriendError[Error: Not friends]
    NotFriendError --> FriendsPage[Redirect to Friends Page]
    
    CheckFriendship -->|Yes| GenerateRoom[Generate Private Room Name<br/>private_user1_user2<br/>sorted alphabetically]
    GenerateRoom --> LoadChat[Load Private Chat Page]
    LoadChat --> LoadHistory[Load Message History<br/>from DirectMessage table]
    LoadHistory --> RenderChat[Render Chat Interface]
    
    RenderChat --> EstablishWS[Establish WebSocket<br/>PrivateMessageConsumer]
    EstablishWS --> AuthCheck{User<br/>Authenticated?}
    AuthCheck -->|No| CloseWS[Close Connection]
    AuthCheck -->|Yes| JoinGroup[Join Private Group<br/>via Redis]
    JoinGroup --> JoinNotifications[Join Notification Group]
    JoinNotifications --> WSReady[WebSocket Ready]
    
    WSReady --> UserSends[User Sends Private Message]
    UserSends --> ReceiveWS[Consumer Receives Message]
    ReceiveWS --> GetRecipient[Get Recipient User Object]
    GetRecipient --> SaveMessage[Save DirectMessage<br/>to Database]
    SaveMessage --> BroadcastPrivate[Broadcast to Private Group<br/>via Redis]
    
    BroadcastPrivate --> NotifyRecipient[Send Notification to<br/>Recipient's Notification Group]
    NotifyRecipient --> RecipientReceives[Recipient Receives Message<br/>in Private Group]
    NotifyRecipient --> RecipientNotified[Recipient Gets Notification<br/>if Not in Chat]
    
    RecipientReceives --> UpdateRecipientUI[Update Recipient UI]
    BroadcastPrivate --> UpdateSenderUI[Update Sender UI]
    
    UpdateRecipientUI --> MarkRead{Mark as Read?}
    UpdateSenderUI --> ContinueChat[Continue Chat]

```


## 5. WebSocket Connection & Message Flow
```mermaid
    flowchart LR
    Client[Browser Client] -->|1. WebSocket Connect| ASGI[ASGI Application]
    ASGI -->|2. Origin Check| OriginValidator[AllowedHostsOriginValidator]
    OriginValidator -->|3. Auth Check| AuthStack[AuthMiddlewareStack]
    AuthStack -->|4. Route| Router[WebSocket Router<br/>chat/routing.py]
    
    Router -->|Route to| Consumer[Consumer<br/>ChatRoom/Private/Notification]
    Consumer -->|5. Connect| AuthUser{User<br/>Authenticated?}
    
    AuthUser -->|No| Close[Close Connection]
    AuthUser -->|Yes| JoinGroup[Join Channel Group<br/>via Redis]
    JoinGroup -->|6. Accept| Accept[Accept WebSocket]
    Accept --> Connected[Connection Established]
    
    Connected -->|7. User Sends Message| Receive[Consumer Receives Message]
    Receive --> Process[Process Message]
    
    Process -->|Save to DB| SaveDB[(Database)]
    Process -->|Broadcast| Redis[(Redis Channel Layer)]
    
    Redis -->|8. Distribute| GroupMembers[All Group Members]
    GroupMembers -->|9. Send| AllClients[All Connected Clients]
    AllClients -->|10. Update UI| Client
    
    Connected -->|Disconnect| Disconnect[User Disconnects]
    Disconnect --> LeaveGroup[Leave Channel Group]
    LeaveGroup --> Cleanup[Cleanup Connection]

```


## 6. Online Status Notification Flow
```mermaid
flowchart TD
    Start([User Logs In]) --> ConnectWS[Connect to NotificationConsumer]
    ConnectWS --> AuthCheck{Authenticated?}
    AuthCheck -->|No| Reject[Reject Connection]
    AuthCheck -->|Yes| CreateGroup[Create Notification Group<br/>notifications_username]
    CreateGroup --> AddToOnline[Add to ONLINE_USERS set]
    AddToOnline --> GetFriends[Get All Friends from Profile]
    GetFriends --> NotifyFriends[Notify Each Friend's Notification Group]
    
    NotifyFriends --> FriendReceives[Friend Receives Status Update<br/>type: status_update<br/>is_online: true]
    FriendReceives --> UpdateFriendUI[Update Friend's UI<br/>Show Online Indicator]
    
    ConnectWS --> SendInitial[Send Initial Status to User]
    SendInitial --> GetOnlineFriends[Get Online Friends from ONLINE_USERS set]
    GetOnlineFriends --> SendList[Send Online Friends List<br/>type: initial_status]
    SendList --> UpdateUserUI[Update User's UI<br/>Show Online Friends]
    
    UpdateUserUI --> UserSendsMessage{User Sends Private Message?}
    UserSendsMessage -->|Yes| TriggerNotification[PrivateMessageConsumer Sends Notification]
    TriggerNotification --> NotifyGroup[Send to Recipient's Notification Group]
    NotifyGroup --> RecipientNotified[Recipient Receives<br/>type: new_message]
    RecipientNotified --> ShowNotification[Show Notification UI]
    
    Start --> Disconnect[User Disconnects]
    Disconnect --> RemoveFromOnline[Remove from ONLINE_USERS]
    RemoveFromOnline --> NotifyOffline[Notify All Friends<br/>is_online: false]
    NotifyOffline --> UpdateOfflineUI[Update Friends' UI<br/>Show Offline]

```


## 7. Complete Message Sending Flow (Detailed)
```mermaid
    flowchart TD
    UserAction([User Types Message<br/>& Clicks Send]) --> JSHandler[JavaScript Handler]
    JSHandler --> FormatMessage[Format Message Data<br/>JSON.stringify]
    FormatMessage --> SendWS[Send via WebSocket<br/>websocket.send]
    
    SendWS --> ASGIReceive[ASGI Receives Message]
    ASGIReceive --> RouteToConsumer[Route to Consumer<br/>based on URL]
    
    RouteToConsumer --> RoomConsumer{Consumer Type?}
    RoomConsumer -->|Room Chat| RoomProcess[ChatRoomConsumer<br/>receive method]
    RoomConsumer -->|Private Chat| PrivateProcess[PrivateMessageConsumer<br/>receive method]
    
    RoomProcess --> RoomSave[Save RoomMessage<br/>to Database]
    RoomSave --> RoomBroadcast[Broadcast to Room Group<br/>channel_layer.group_send]
    
    PrivateProcess --> GetRecipient[Get Recipient User]
    GetRecipient --> PrivateSave[Save DirectMessage<br/>to Database]
    PrivateSave --> PrivateBroadcast[Broadcast to Private Group<br/>channel_layer.group_send]
    PrivateBroadcast --> NotifyRecipient[Send Notification to<br/>Recipient Group]
    
    RoomBroadcast --> RedisReceive[Redis Receives Message]
    PrivateBroadcast --> RedisReceive
    NotifyRecipient --> RedisReceive
    
    RedisReceive --> DistributeToGroup[Distribute to All<br/>Group Members]
    DistributeToGroup --> ConsumerReceive[Each Consumer's<br/>chat_message/private_message method]
    
    ConsumerReceive --> CheckSender{Is This<br/>The Sender?}
    CheckSender -->|Yes| SkipSend[Skip Sending<br/>Avoid Echo]
    CheckSender -->|No| SendToClient[Send to Client<br/>via WebSocket]
    
    SendToClient --> ClientReceives[Browser Receives Message]
    ClientReceives --> ParseJSON[Parse JSON Data]
    ParseJSON --> RenderMessage[Render Message in UI]
    RenderMessage --> ScrollToBottom[Scroll Chat to Bottom]
    
    SkipSend --> End([End])
    ScrollToBottom --> End

```
