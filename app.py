elif menu=="Poultry Batches":
    st.subheader("Poultry Batch Management / মুরগির ব্যাচ")

    with st.form("pb"):
        x1,x2=st.columns(2)
        name=x1.text_input("Batch name / ব্যাচের নাম")
        typ=x2.selectbox(
            "Bird type / মুরগির ধরন",
            ["Color Bird","Fumi","Broiler","Layer","Other"]
        )
        x3,x4=st.columns(2)
        sd=x3.date_input("Start date / শুরুর তারিখ",date.today())
        qty=x4.number_input(
            "Opening chicks / প্রাথমিক বাচ্চা",
            min_value=1,step=1
        )
        cost=st.number_input(
            "Chick purchase cost (BDT)",
            min_value=0.0
        )
        notes=st.text_area("Notes / মন্তব্য")

        if st.form_submit_button("Save batch / ব্যাচ সংরক্ষণ"):
            if name.strip():
                run(
                    """INSERT INTO poultry_batches
                    (batch_name,bird_type,start_date,opening_birds,purchase_cost,notes)
                    VALUES(?,?,?,?,?,?)""",
                    (name.strip(),typ,str(sd),qty,cost,notes)
                )
                st.success("Batch saved successfully.")
                st.rerun()
            else:
                st.error("Batch name is required.")

    st.divider()
    st.subheader("Saved Poultry Batches / সংরক্ষিত ব্যাচ")

    rows=q("SELECT * FROM poultry_batches ORDER BY id DESC")

    if rows:
        df=pd.DataFrame([dict(x) for x in rows])
        st.dataframe(df,use_container_width=True)

        opts={
            f'ID {x["id"]} | {x["batch_name"]} | {x["bird_type"]}':
            x["id"] for x in rows
        }

        selected=st.selectbox(
            "Select batch to Edit or Delete",
            list(opts.keys()),
            key="selected_poultry_batch"
        )
        batch_id=opts[selected]

        batch=q(
            "SELECT * FROM poultry_batches WHERE id=?",
            (batch_id,)
        )[0]

        st.markdown("### Edit Batch / ব্যাচ সংশোধন")

        with st.form("edit_poultry_batch"):
            new_name=st.text_input(
                "Batch name",
                value=batch["batch_name"] or ""
            )
            types=["Color Bird","Fumi","Broiler","Layer","Other"]
            old_type=batch["bird_type"] or "Other"
            type_index=types.index(old_type) if old_type in types else 4
            new_type=st.selectbox(
                "Bird type",types,index=type_index
            )
            new_date=st.date_input(
                "Start date",
                value=date.fromisoformat(batch["start_date"])
                if batch["start_date"] else date.today()
            )
            new_qty=st.number_input(
                "Opening chicks",
                min_value=1,
                value=max(1,int(batch["opening_birds"] or 1))
            )
            new_cost=st.number_input(
                "Purchase cost",
                min_value=0.0,
                value=float(batch["purchase_cost"] or 0)
            )
            new_notes=st.text_area(
                "Notes",
                value=batch["notes"] or ""
            )

            if st.form_submit_button("Update Batch / সংশোধন সংরক্ষণ"):
                if new_name.strip():
                    run(
                        """UPDATE poultry_batches
                        SET batch_name=?,bird_type=?,start_date=?,
                        opening_birds=?,purchase_cost=?,notes=?
                        WHERE id=?""",
                        (
                            new_name.strip(),new_type,str(new_date),
                            new_qty,new_cost,new_notes,batch_id
                        )
                    )
                    st.success("Batch updated successfully.")
                    st.rerun()
                else:
                    st.error("Batch name is required.")

        st.divider()
        st.markdown("### Delete Batch / ব্যাচ মুছুন")

        daily_count=q(
            "SELECT COUNT(*) AS total FROM poultry_daily WHERE batch_id=?",
            (batch_id,)
        )[0]["total"]

        if daily_count > 0:
            st.warning(
                f"This batch has {daily_count} daily records. "
                "Delete is blocked to protect your farm records."
            )
        else:
            confirm=st.checkbox(
                f"I confirm deletion of Batch ID {batch_id}",
                key=f"confirm_delete_batch_{batch_id}"
            )

            if st.button(
                "Delete Selected Batch / নির্বাচিত ব্যাচ মুছুন",
                type="primary",
                disabled=not confirm
            ):
                run(
                    "DELETE FROM poultry_batches WHERE id=?",
                    (batch_id,)
                )
                st.success("Batch deleted successfully.")
                st.rerun()
    else:
        st.info("No poultry batches found.")
