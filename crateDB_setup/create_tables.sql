-- 1. Customers table (parent)
CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  name TEXT,
  email TEXT,
  registration_date TIMESTAMP,
  address OBJECT(DYNAMIC)
);

-- 2. Categories table (parent)
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name TEXT,
  description TEXT
);

-- 3. Products table (child of categories)
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT,
  description TEXT,
  category_id INTEGER,
  price DOUBLE PRECISION,
  stock_quantity INTEGER,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 4. Orders table (child of customers)
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  order_date TIMESTAMP,
  status TEXT,
  total_amount DOUBLE PRECISION,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- 5. Order_items table (junction between orders and products)
CREATE TABLE order_items (
  order_id INTEGER,
  product_id INTEGER,
  quantity INTEGER,
  unit_price DOUBLE PRECISION,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);