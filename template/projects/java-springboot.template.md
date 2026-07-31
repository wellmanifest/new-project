# Wzorzec Projektowy: Java Spring Boot (`java-springboot`)

Manifest jednoplikowy opisujący aplikację Spring Boot budowaną Mavenem.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa projektu | `orders` |
| `group_id` | GroupId Maven | `com.example` |
| `package_path` | Ścieżka pakietu | `com/example/orders` |
| `main_class` | Klasa główna | `OrdersApplication` |

## Manifest

```yaml
variables:
  project_name: orders
  group_id: com.example
  package_path: com/example/orders
  main_class: OrdersApplication

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/src/main/java/{{ package_path }}"
  - "{{ project_name }}/src/main/resources"
  - "{{ project_name }}/src/test/java/{{ package_path }}"

files:
  - path: "{{ project_name }}/pom.xml"
    type: config
    contents: |
      <?xml version="1.0" encoding="UTF-8"?>
      <project xmlns="http://maven.apache.org/POM/4.0.0"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>
        <parent>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-starter-parent</artifactId>
          <version>3.3.3</version>
        </parent>
        <groupId>{{ group_id }}</groupId>
        <artifactId>{{ project_name }}</artifactId>
        <version>0.1.0</version>
        <properties><java.version>21</java.version></properties>
        <dependencies>
          <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
          </dependency>
          <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
          </dependency>
        </dependencies>
        <build>
          <plugins>
            <plugin>
              <groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
          </plugins>
        </build>
      </project>

  - path: "{{ project_name }}/src/main/java/{{ package_path }}/{{ main_class }}.java"
    type: source
    contents: |
      package {{ group_id }}.{{ project_name }};

      import org.springframework.boot.SpringApplication;
      import org.springframework.boot.autoconfigure.SpringBootApplication;

      @SpringBootApplication
      public class {{ main_class }} {
          public static void main(String[] args) {
              SpringApplication.run({{ main_class }}.class, args);
          }
      }

  - path: "{{ project_name }}/src/main/java/{{ package_path }}/HealthController.java"
    type: source
    contents: |
      package {{ group_id }}.{{ project_name }};

      import org.springframework.web.bind.annotation.GetMapping;
      import org.springframework.web.bind.annotation.RestController;
      import java.util.Map;

      @RestController
      public class HealthController {
          @GetMapping("/health")
          public Map<String, String> health() {
              return Map.of("status", "ok");
          }
      }

  - path: "{{ project_name }}/src/main/resources/application.properties"
    type: config
    contents: |
      server.port=8080
      spring.application.name={{ project_name }}

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      target/
      *.class
      .idea/
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `mvn spring-boot:run`.
