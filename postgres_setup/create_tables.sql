CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    registration_date TIMESTAMP,
    street TEXT,
    city TEXT,
    zip TEXT
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    category_id INTEGER,
    price DOUBLE PRECISION,
    stock_quantity INTEGER
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP,
    status TEXT,
    total_amount DOUBLE PRECISION
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DOUBLE PRECISION,
    PRIMARY KEY (order_id, product_id)
);
