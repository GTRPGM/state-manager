# HTTP란?

> 미리 정해진 요청과 응답 형식에 따라 통신하고 처리결과를 의미있는 숫자로 알려주는 규칙이자, 상태코드 기반의 프로토콜.

아래와 같은 과정을 거쳐서 HTTP의 통신과정이 진행된다.

1. Client(사용자)가 요청을 생성한다
2. 요청이 서버로 보내진다
3. 서버가 요청을 처리한다
4. 처리결과를 숫자에 매핑한다
5. 숫자와 응답을 함께 돌려준다

### 비슷하지만 다른 용도의 용어들

| 용어 | 설명 |
|------|------|
| HTTP | 규칙 |
| HTTP/1.1, HTTP/2 | 규칙의 버전 |
| HTTPS | 암호화된 HTTP |
| HTTPX | HTTP 사용 도구 |

---

# HTTP 전체 통신흐름

1. 요청생성
2. 전송 및 핸들링
3. 라우터 요청 매핑
4. 비즈니스 로직 처리
5. 응답 생성 및 반환

**특수처리 매커니즘**: 커넥션 풀링 및 비동기 수신 / 인증 해더 주입 / 타임아웃 핸들링 / 예외상태 및 상태 코드 매칭

---

## 1. 요청생성(Request Creation)

> client(브라우저/앱/서버)의 입력을 서버가 이해할 수 있는 HTTP 요청 객체의 형태로 가공하는 단계

### 구성

- **Method**(GET, POST... etc): 어떤 행동을 할 것인지를 지정
- **URL/Path/Query**: 행동 대상을 지정
- **Headers**(형식/인증정보..etc): 부가설명
- **Body**: 실제로 전달할 내용

### 예시

```
# 사용자의 입력
"로그인 상태로 ID 3인 유저 정보를 가져올래"
                   ↓
# 요청사항 가공
행동?= 조회= GET
어디?= /user_id/3
누가?= 현재 인증토큰이
형식?= JSON
                   ↓
# 생성되는 HTTP 요청
GET /user_id/3 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
User-Agent: Mozilla/5.0
```

### 연관 기술

#### ▶ 인증 헤더 주입(Authentication Header Injection)

> 서버가 요청자에 대해 식별할 수 있도록, 최초 인증과정을 통해 토큰을 발행해서 요청에 토큰을 자동으로 주입하게 하는 방식.

**장점**: 토큰 검증을 통해 사용자 고유의 context를 복원할 수 있다.

```
Authorization: Bearer <JWT>
Cookie: session_id=...
```

#### ▶ 타임아웃 설정(Client-side Timeout)

> 서버 장애나 네트워크 단절시 무한 대기상황을 방지 / 리소스 점유를 방지하기 위해 사용하는 방법으로, 소켓/요청시간에 대해 제한선을 두고 초과시 강제로 종료하는 방식이다.

```
요청 보냄 → T초 대기 → 응답 없으면 Abort
```

---

## 2. 전송 및 핸들링(Transmission & Handling)

> 생성된 HTTP 요청을 서버에 안전하게 전달하고, 서버가 이를 받아서 해석할 수 있도록 준비하는 단계

### 구성

- **TCP**: 요청과 응답이 순서대로, 누락없이 도착하도록 책임지는 역할
- **TLS**: HTTPS인 경우에 사용되며, 전달 내용 암호화 및 서버 신원 확인 역할
- **Request 전송**: 생성된 HTTP 요청을 네트워크를 통해 서버에 이동시키는 역할
- **서버 수신 및 Parsing**: 수신된 요청에 대해, 분해해서 이해하는 역할

### 예시

```
HTTP 요청 생성
→ TCP : client와 서버의 연결 확보 & 같은 서버로 전달하는 경우에 같은 연결을 사용(connection pool)
→ 암호화
→ 서버로 전송
→ 서버 소켓 수신
→ HTTP 요청 파싱
→ 다음 단계로 전달
```

### 네트워크 흐름

```
[client 프로그램]
        ↓
[client OS 커널]
        ↓
[client 네트워크 인터페이스]
        ↓
     (인터넷)
        ↓
[server 네트워크 인터페이스]
        ↓
   [server OS 커널]
        ↓
   [소켓: server]
        ↓
   [프로그램 코드]
        ↓  ------- 여기부터 HTTP
     [router]
        ↓
   [비즈니스 로직]
```

### 연관 기술

#### ▶ 커넥션 풀링(Connection Pooling)

> 같은 서버로 보내야할 요청에 대비해서, 처음 요청을 전달하면서 생성했던 연결을 pool에 보관하고 요청이 들어오면 재사용하는 방식

**장점**:
- TCP/TLS 연결 생성 비용 감축과 성능 개선
- 서버 부하 및 Latency 감소
- 처리량(ThroughPut) 증가

**HTTP/2의 경우**: 하나의 커넥션에 다중 스트림되면서 pool = 스트림 관리로 확장된다

#### ▶ 비동기 수신(Async / Non-blocking IO)

> 요청 받은 IO에 대해 스레드를 사용해서 DB에 요청을 보내고 요청이 돌아오기 전까지 스레드를 반납해서 여러 요청에 대응 가능하도록 만드는 방식

**장점**: 스레드 점유율을 줄여서 대규모 트래픽에 대응할 수 있다

```
요청 수신
→ DB 요청
→ 스레드 반납
→ DB 응답 이벤트
→ 처리 재개
```

**예시**: Node.js, Netty, Spring WebFlux

---

## 3. 라우터(Router) 요청 매핑

> parsing 받은 HTTP요청을 기준으로, 해당 요청을 처리할 프로그램 내부 핸들러(controler/function)을 결정하는 단계

### 구성

- Method
- Path
- (선택) Query | Header | Connection-Type

### 예시

```
HTTP 요청 파싱 완료
→ Method / Path 추출
→ 라우팅 테이블 조회
→ 매칭되는 핸들러 선택
→ 요청 컨텍스트 생성
→ 비즈니스 로직으로 전달
```

**실제 구현**:
```
GET /users/3
GET /users/{id} → UserController.getUser(id=3)
```

### 연관기술

#### ▶ 라우팅 테이블(Routing Table)

> HTTP Method와 Path를 기준으로 요청 처리 핸들러를 미리 등록한 형태를 의미한다.

**장점**: 요청 분기 로직을 중앙화할 수 있고 유지보수 및 확장에 용이하다

```
GET    /users/{id}   → getUser
POST   /users        → createUser
DELETE /users/{id}   → deleteUser
```

#### ▶ Path Variable / Query Mapping

> URL에 포함된 값을 파라미터로 분해하여 핸들러 함수의 입력값으로 전달하는 방식

**장점**: 재사용 가능한 URL 및 요청 의미를 URL로 표현할 수 있다

```
/users/3 → id = 3
```

#### ▶ 라우팅 실패 처리 (404 / 405)

> 요청과 매칭되는 핸들러가 없는 경우, 비즈니스 로직으로 진입하지 않고 즉시 매핑된 에러 응답을 반환하는 방식

**장점**: 불필요한 로직 실행을 방지하고, 요청오류를 조기에 차단시킬 수 있다

| 상황 | HTTP status |
|------|-------------|
| 경로 없음 | 404 Not Found |
| Method 불일치 | 405 Method Not Allowed |

#### ▶ 미들웨어(Middleware) / 인터셉터(Interceptor) 진입 지점

> 라우터 전·후에서 모든 요청에 공통적으로 수행해야하는 작업을 집어넣는 확장 지점

- **Middleware**: 요청이 라우터로 도달하기 전의 공통작업 (ex. 인증토큰 검사/CORS 처리/공통 헤더 주입 등)
- **Interceptor**: 라우터가 지정한 핸들러의 실행 전/후에 개입하는 중간장치(ex. 실행시간 측정/로그기록/토큰기록 등)

**프레임워크 별 이름**:
| 프레임워크 | 명칭 |
|------------|------|
| Express | middleware |
| Spring | filter / interceptor |
| FastAPI | dependency / middleware |
| Netty | handler |

**작업 종류**:
- **공통검증(Common_Validation)**: 요청의 형식이 알맞는지 확인하는 작업 → Middleware
- **인증(Authentication)**: 요청자에 대해 식별하는 작업 → Middleware | Business Logic
- **logging**: 요청/처리/응답에 대한 기록을 남기는 작업 → Interceptor

**장점**: 불필요한 로직 실행을 방지하고, 요청오류를 조기에 차단, 코드 단순화가 가능하다.

```
요청
→ (공통 검증 / 인증 Middleware)
→ Router
→ (로깅 Interceptor - 시작)
→ 비즈니스 로직
→ (로깅 Interceptor - 종료)
→ 응답
```

---

## 4. 비즈니스 로직 처리(Business Logic Processing)

> 라우터가 선택한 핸들러 내부에서 요청을 해석하고 실제 일을 수행하는 단계

### 구성

- **인증/권한(Authentication/Authorization)**: 요청자에 대해 식별하고, 이 행동에 대한 권한이 있는지를 확인
- **데이터 검증**: 요청 데이터가 도메인 규칙(비즈니스 규칙)을 위반하지 않는지 확인
- **도메인 로직 수행**
- **외부 시스템 호출(DB/API)**: 다른 DB나 서버(API), 캐시(Redis)에 접근

### 예시

```
요청 도착
→ 권한 확인
→ 유저 존재 여부 검증
→ 유저 정보 조회 (DB)
→ 도메인 규칙 적용
→ 결과 반환
```

### 연관 기술

#### ▶ 타임아웃 핸들링(Server-side)

> 외부 의존 호출과정에서 사용되며, 호출 제한시간을 부여하고 초과 시에 즉시 실패처리하는 방식

**장점**:
- 장애전파 방지
- 시스템 연쇄 붕괴 방지(Cascading Failure)

```
외부 호출 → T초 초과 → 예외 발생
```

#### ▶ 예외상태 매핑(Exception Mapping)

> 비즈니스 로직 내부에 사용되며, 내부예외를 의미있는 도메인 오류로 변환한 다음 HTTP Status로 매핑한다

**장점**: 내부 오류코드를 그대로 노출하면 안되는 경우에 사용한다.

```
UserNotFoundException
→ 404 Not Found
```

---

## 5. 응답 생성 및 반환(Response Creation & Delivery)

> 비즈니스 로직의 처리결과를 클라이언트가 이해할 수 있는 HTTP응답 형태로 변환해 돌려주는 단계

### 구성

- **Status Code 설정**: 처리결과를 숫자 상태코드로 요약해서 클라이언트가 성공/실패를 1차적으로 판단할 수 있게 한다.
- **Header 구성**: 응답에 대해 Content-Type이나 CORS 관련 헤더와 같은 부가 정보를 전달한다.
- **Body 구성**: 실제 응답 데이터를 의미한다. 보통 JSON 형식
- **Client에 전송**: 네트워크 흐름에 맞춰 client에게 반환

### 예시

```
비즈니스 로직 완료
→ 결과 객체 생성
→ HTTP Status 결정
→ Header / Body 구성
→ 응답 전송
```

### 연관 기술

#### ▶ 상태 코드 매핑(Status code mapping)

> 로직 처리결과를 HTTP 의미 체계에 맞는 숫자로 매핑하는 방식

**Why?**: Body를 확인하기 전에 client의 분기는 HTTP 상태코드를 기준으로 정해지기 때문에, 매핑이 필수적이다.

**※ 에러코드 작성시 유의사항 ※**

> 불필요한 상태코드를 지양하고, HTTP 규칙을 최대한 준수하면서 작성하는 REST 스타일의 응답설계를 지향하는 것이 좋다.

| 상황 | HTTP Status |
|------|-------------|
| 성공 | 200/201 |
| 인증실패 | 401 |
| 권한없음 | 403 |
| 리소스 없음 | 404 |
| 서버 오류 | 500 |

#### ▶ 예외 응답 표준화

> 응답직전에 사용되며, 모든 에러 응답을 일관된 구조로 매핑하는 방식

**장점**:
- 클라이언트에게 parsing할때 안정성을 높여준다
- 에러처리의 일관성을 확보할 수 있다

```json
{
  "code": "USER_NOT_FOUND",
  "message": "User does not exist"
}
```
