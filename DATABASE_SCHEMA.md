# Database Schema

## Entity Relationship Diagram

```
User (users)
│
├── Cart (carts) [1:1 via user_id]
│   └── CartItem (cart_items) [1:N via cart_id]
│       └── Product (products) [N:1 via product_id]
│
└── Order (orders) [1:N via user_id]
    ├── OrderItem (order_items) [1:N via order_id]
    │   └── Product (products) [N:1 via product_id]
    └── Payment (payments) [1:1 via order_id]
```

## Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| email | VARCHAR(255) UNIQUE | |
| username | VARCHAR(100) UNIQUE | |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| google_id | VARCHAR(255) UNIQUE | |
| role | ENUM | CUSTOMER, ADMIN |
| is_active | BOOLEAN | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### products
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | VARCHAR(255) | |
| description | TEXT | |
| price | FLOAT | >= 0 |
| image_url | VARCHAR(500) | |
| category | VARCHAR(100) | |
| stock_quantity | INTEGER | >= 0 |
| is_active | BOOLEAN | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### carts
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK → users.id UNIQUE | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### cart_items
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| cart_id | INTEGER FK → carts.id | |
| product_id | INTEGER FK → products.id | |
| quantity | INTEGER | > 0 |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### orders
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK → users.id | |
| total_amount | FLOAT | Backend-calculated |
| status | ENUM | PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED |
| payment_status | ENUM | PENDING, PAID, FAILED, CANCELLED |
| stripe_session_id | VARCHAR(255) UNIQUE | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### order_items
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| order_id | INTEGER FK → orders.id | |
| product_id | INTEGER FK → products.id | |
| product_name | VARCHAR(255) | Snapshot at order time |
| price | FLOAT | Snapshot at order time |
| quantity | INTEGER | |
| subtotal | FLOAT | price × quantity |
| created_at | DATETIME | |

### payments
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| order_id | INTEGER FK → orders.id UNIQUE | |
| stripe_payment_intent_id | VARCHAR(255) UNIQUE | |
| stripe_session_id | VARCHAR(255) UNIQUE | |
| amount | FLOAT | |
| currency | VARCHAR(10) | |
| status | ENUM | PaymentStatus |
| created_at | DATETIME | |
| updated_at | DATETIME | |

## Business Rules

- New Google users always get role `CUSTOMER`
- Admin users are created via seed script or database
- OrderItem stores product name/price at order time (price history preserved)
- Stock is reduced only after Stripe webhook confirms payment
- Cart is cleared after successful payment webhook
