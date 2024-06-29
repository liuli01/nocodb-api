from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nocodb import NocoDB


from nocodb.Table import Table


class Base:
    def __init__(self, noco_db: "NocoDB",
                 **kwargs) -> None:

        self.noco_db = noco_db
        self.base_id = kwargs["id"]
        self.title = kwargs["title"]
        self.metadata = kwargs

    def duplicate(self,
                  exclude_data: bool = True,
                  exclude_views: bool = True,
                  exclude_hooks: bool = True
                  ) -> "Base":

        r = self.noco_db.call_noco(path=f"meta/duplicate/{self.base_id}",
                                   method="POST",
                                   json={
            "excludeData": exclude_data,
            "excludeViews": exclude_views,
            "excludeHooks": exclude_hooks})

        return self.noco_db.get_base(base_id=r.json()["base_id"])

    def delete(self) -> bool:
        r = self.noco_db.call_noco(path=f"meta/bases/{self.base_id}",
                                   method="DELETE")
        return r.json()

    def update(self, **kwargs) -> None:
        self.noco_db.call_noco(path=f"meta/bases/{self.base_id}",
                               method="PATCH",
                               json=kwargs)

    def get_base_info(self) -> dict:
        r = self.noco_db.call_noco(path=f"meta/bases/{self.base_id}/info")
        return r.json()

    def get_tables(self) -> list[Table]:
        r = self.noco_db.call_noco(path=f"meta/bases/{self.base_id}/tables")
        return [Table(base=self, **t) for t in r.json()["list"]]

    def get_table(self, table_id: str) -> Table:
        r = self.noco_db.call_noco(
            path=f"meta/tables/{table_id}")
        return Table(base=self, **r.json())

    def get_table_by_title(self, title: str) -> Table:
        try:
            return next((b for b in self.get_tables() if b.title == title))
        except StopIteration:
            raise Exception(f"Table with name {title} not found!")

    def create_table(self, table_name: str,
                     columns: list[dict] = [{"column_name": "title"}], **kwargs) -> Table:
        kwargs["table_name"] = table_name
        kwargs["columns"] = columns

        r = self.noco_db.call_noco(path=f"meta/bases/{self.base_id}/tables",
                                   method="POST",
                                   json=kwargs)
        return self.get_table(table_id=r.json()["id"])