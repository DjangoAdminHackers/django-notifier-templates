var table_attrs = "bgcolor|border|cellspacing|cellpadding|align|width|height";

site_mce_config = {
  "content_css": '/static/css/mce_styles.css',
  "theme_advanced_buttons1": "formatselect,removeformat,|,bold,italic,|,bullist,numlist,|,undo,redo,|,link,unlink",
  "valid_elements": ("a[href],-h2/h1,-h3/h4/h5,p,ul,-li,-ol,br,-em/i,-strong/b,-span,hr,table[_table_attrs_],tr[_table_attrs_],th[_table_attrs_],td[_table_attrs_],thead[_table_attrs_],tbody[_table_attrs_]").replace(/_table_attrs_/g, table_attrs)
};

