fazer login na plataforma
https://rodogarcia.eslcloud.com.br/users/sign_in

**IMPORTANTE:** Credenciais devem ser configuradas no arquivo `.env`, nunca no código ou na documentação.

Elementos a localizar:
- Campo de email: `#user_email` (ou `input[name='user[email]']`)
- Campo de senha: `#user_password` (ou `input[name='user[password]']`)
- Botão entrar: `input[type='submit'][value='Entrar']`



1 - clicar em cadastros (menu)

<a href="javascript:;" tabindex="-1">Cadastros</a>

2 - tabelas de preco (menu)

<a href="javascript:;" tabindex="-1"><i class="fa fa-money-bill-alt"></i><span class="text-icon ">Tabelas de preço</span></a>

3 - tabelas de cliente (menu)

<a href="/customer_price_tables" tabindex="-1">Tabelas de cliente</a>


(ambos acima sao do menu da tela inicial)
proxima pagina agora a seguir


passos 4, 5 e 6 sao dentro desse codigo abaixo

<div class="portlet-body"><form id="search_form" class="simple_form  vuejs" novalidate="novalidate" action="javascript:;" accept-charset="UTF-8" method="post"><input name="utf8" type="hidden" value="✓" autocomplete="off"><input type="hidden" name="authenticity_token" value="Qmdb3HMsLaGGBaN2eLBLq0qBXKV3hfSOFGx5S6aexrIVOvtJa0FuYe4hKrjSqt3fLJTAWaXgulwjGDUupXvuJQ" autocomplete="off"><div class="row main-filters"><div class="col-sm-11-quarter"><div class="row"><div class="col-sm-2"><div class="form-group select optional search_price_tables_corporation"><label class="select optional" for="search_price_tables_corporation_id">Filial Responsável</label><input name="search[price_tables][corporation_id][]" type="hidden" value="" autocomplete="off"><select class="form-control select optional input-sm select2-base select2-hidden-accessible" multiple="" name="search[price_tables][corporation_id][]" id="search_price_tables_corporation_id" tabindex="-1" aria-hidden="true"><option value="385128">AGU - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="619080">ARQ - ATF TRANSPORTES E LOGISTICA | PARCEIRO ARARAQUARA</option>
<option value="597545">CAC - TRIUNFO TRANSPORTES | PARCEIRO CASCAVEL</option>
<option value="385131">CAS - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="385217">CPQ - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="624660">CTV - BOSS EXPRESS | PARCEIRO CATANDUVA</option>
<option value="385133">CWB - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="599169">FBO - RAFA TRANSPORTES | PARCEIRO FRANCISCO BELTRÃO</option>
<option value="619400">FRC - CR TRANPORTES | PARCEIRO RIBEIRÃO PRETO</option>
<option value="603006">GUA - TIGER TRANSPPORTES | PARCEIRO GUARAPUAVA</option>
<option value="617950">JCR - TRANSPORTADORA JACAREI | PARCEIRO JACAREÍ</option>
<option value="610216">LDN - K.E.M. LOG | PARCEIRO LONDRINA</option>
<option value="385125">MTZ - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="385220">NHB - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="599713">PTO - NEW TRANSPORTES | PARCEIRO PATO BRANCO</option>
<option value="385227">REC - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="385229">RJR - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="433115">RODOGAR LOCACAO E SERVICOS</option>
<option value="624659">SJP - R.A BEGGIORA | PARCEIRO SÃO JOSE DO RIO PRETO</option>
<option value="385129">SPO - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</option>
<option value="468288">TR RODOGARCIA | AGU</option>
<option value="468314">TR RODOGARCIA | CAS</option>
<option value="468296">TR RODOGARCIA | CPQ</option>
<option value="468322">TR RODOGARCIA | CWB</option>
<option value="468331">TR RODOGARCIA | NHB</option>
<option value="468334">TR RODOGARCIA | REC</option>
<option value="468341">TR RODOGARCIA | RJR</option>
<option value="421028">TR RODOGARCIA | SPO</option></select><span class="select2 select2-container select2-container--default select2-container--below" dir="ltr" style="width: 166px;"><span class="selection"><span class="select2-selection select2-selection--multiple" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="-1"><ul class="select2-selection__rendered"><li class="select2-search select2-search--inline"><input class="select2-search__field" type="search" tabindex="0" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" role="textbox" aria-autocomplete="list" placeholder="Selecione" style="width: 164px;"></li></ul></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group string optional search_price_tables_name"><label class="string optional" for="search_price_tables_name">Nome</label><input class="form-control string optional input-sm" type="text" name="search[price_tables][name]" id="search_price_tables_name"></div></div><div class="col-sm-2"><div class="has-list-modal form-group select optional search_person_price_tables_person"><label class="select optional" for="search_person_price_tables_person_id">Cliente</label><a class="pull-right listModal" data-remote="true" href="/people?caller=preview_modal" tabindex="-1"><i class="fa fa-search"></i></a><select class="form-control select optional input-sm customer-autocomplete allow-clear select2-hidden-accessible" name="search[person_price_tables][person_id]" id="search_person_price_tables_person_id" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option class="vue-option" value=""></option></select><span class="select2 select2-container select2-container--default" dir="ltr" style="width: 166px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_person_price_tables_person_id-container"><span class="select2-selection__rendered" id="select2-search_person_price_tables_person_id-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group select optional search_price_table_locations_origin_location"><label class="select optional" for="search_price_table_locations_origin_location_id">Origem</label><select class="form-control select optional input-sm city-autocomplete allow-clear select2-hidden-accessible" data-polymorphic="true" name="search[price_table_locations][origin_location_id]" id="search_price_table_locations_origin_location_id" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option class="vue-option" value=""></option></select><span class="select2 select2-container select2-container--default" dir="ltr" style="width: 166px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_price_table_locations_origin_location_id-container"><span class="select2-selection__rendered" id="select2-search_price_table_locations_origin_location_id-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group select optional search_price_table_locations_destination_location"><label class="select optional" for="search_price_table_locations_destination_location_id">Destino</label><select class="form-control select optional input-sm city-autocomplete allow-clear select2-hidden-accessible" data-polymorphic="true" name="search[price_table_locations][destination_location_id]" id="search_price_table_locations_destination_location_id" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option class="vue-option" value=""></option></select><span class="select2 select2-container select2-container--default" dir="ltr" style="width: 166px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_price_table_locations_destination_location_id-container"><span class="select2-selection__rendered" id="select2-search_price_table_locations_destination_location_id-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group select optional search_price_tables_active"><label class="select optional" for="search_price_tables_active">Ativa</label><select class="form-control select optional input-sm select2-base select2-hidden-accessible" name="search[price_tables][active]" id="search_price_tables_active" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option value="true">Sim</option>
<option value="false">Não</option></select><span class="select2 select2-container select2-container--default select2-container--below select2-container--focus" dir="ltr" style="width: 166px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_price_tables_active-container"><span class="select2-selection__rendered" id="select2-search_price_tables_active-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div></div></div><div class="col-sm-0-three-quarters"><span class="input-group-btn filter-group"><button tabindex="-1" id="submit" class="btn btn-primary vue-button btn-sm" type="submit"><i class="fa fa-search"></i></button><button tabindex="-1" class="btn btn-primary vue-button btn-sm" type="button"><i class="fa fa-angle-down"></i></button></span></div></div><div class="row secondary-filters" style="display: none;"><div class="col-sm-11-quarter"><div class="row"><div class="col-sm-2"><div class="form-group select optional search_price_tables_modal"><label class="select optional" for="search_price_tables_modal">Modal</label><select class="form-control select optional input-sm select2-base allow-clear select2-hidden-accessible" name="search[price_tables][modal]" id="search_price_tables_modal" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option value="air">Aéreo</option>
<option value="rodo">Rodoviário</option>
<option value="all">Todos</option></select><span class="select2 select2-container select2-container--default" dir="ltr" style="width: 100px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_price_tables_modal-container"><span class="select2-selection__rendered" id="select2-search_price_tables_modal-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group select optional search_price_tables_range_type"><label class="select optional" for="search_price_tables_range_type">Faixa principal</label><select class="form-control select optional input-sm select2-base allow-clear select2-hidden-accessible" name="search[price_tables][range_type]" id="search_price_tables_range_type" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option value="taxed_weight">Peso taxado</option>
<option value="cubed_weight">Peso cubado</option>
<option value="real_weight">Peso real</option>
<option value="km">Km</option>
<option value="invoices_volumes">Volumes</option>
<option value="invoices_value">Valor NF</option>
<option value="cubic_volume">M3</option>
<option value="invoices_product_quantity">Produtos</option></select><span class="select2 select2-container select2-container--default" dir="ltr" style="width: 100px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_price_tables_range_type-container"><span class="select2-selection__rendered" id="select2-search_price_tables_range_type-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group select optional search_price_tables_price_table_service_type"><label class="select optional" for="search_price_tables_price_table_service_type_id">Tipo de Serviço</label><select class="form-control select optional input-sm price-table-service-type-autocomplete select2-hidden-accessible" name="search[price_tables][price_table_service_type_id]" id="search_price_tables_price_table_service_type_id" tabindex="-1" aria-hidden="true"><option value="" label=" "></option>
<option class="vue-option" value=""></option></select><span class="select2 select2-container select2-container--default" dir="ltr" style="width: 100px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-labelledby="select2-search_price_tables_price_table_service_type_id-container"><span class="select2-selection__rendered" id="select2-search_price_tables_price_table_service_type_id-container"><span class="select2-selection__placeholder">Selecione</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span></div></div><div class="col-sm-2"><div class="form-group string optional search_price_tables_code"><label class="string optional" for="search_price_tables_code">Código</label><input class="form-control string optional input-sm" type="text" name="search[price_tables][code]" id="search_price_tables_code"></div></div><div class="col-sm-2"><div class="form-group date_range optional search_price_tables_effective_until"><label class="date_range optional" for="search_price_tables_effective_until">Válida até</label><span class="date-range right"><input class="form-control date_range optional date-range-picker form-control input-sm input-sm masked" type="text" name="search[price_tables][effective_until]" id="search_price_tables_effective_until"></span></div></div></div></div></div></form></div>


4 - Filical responsavel - desmarcar a opcao que esta dentro do input clicando no x na direita

<ul class="select2-selection__rendered"><span class="select2-selection__clear">×</span><li class="select2-selection__choice" title="SPO - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA"><span class="select2-selection__choice__remove" role="presentation">×</span>SPO - RODOGARCIA TRANSPORTES RODOVIARIOS LTDA</li><li class="select2-search select2-search--inline"><input class="select2-search__field" type="search" tabindex="0" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" role="textbox" aria-autocomplete="list" placeholder="" style="width: 0.75em;"></li></ul>

5 - Ativa - clicar e selecionar a primeira opcao "Sim"

<span class="select2-selection__rendered" id="select2-search_price_tables_active-container"><span class="select2-selection__placeholder">Selecione</span></span>

<span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span>

6 - clicar no botao pesquisar

<button tabindex="-1" id="submit" class="btn btn-primary vue-button btn-sm" type="submit"><i class="fa fa-search"></i></button>


agora proximos passos serao dentro da tabela renderizada
<tr class="vue-item" data-id="55852" row_key="0">


7 - agora localizado nessa coluna terao botoes para ser clicar e com funcoes especificas

<th class="vue-actions-column text-center"> <a class="green-dark btn-outline btn vue-button" style="padding: 2px 5px" title="Exportar" id="btn-export-xlsx" tabindex="-1"> <i class="fa fa-file-excel"></i> </a> </th>

8 - seta para baixo para aparecer mais informacoes

<button type="button" style="max-width: 25px;" class="btn blue-chambray btn-outline btn-xs dropdown-toggle more-actions vue-dropdown-item no-margin-right" data-toggle="dropdown"><i class="fa fa-angle-down"></i></button>


9 - apos aparecer as informacoes, scrolar ate encontrar reajuste e clicar nele

<a class="dropdown-link"><i class="fa fa-chart-line font-yellow-gold"></i><span class="text-icon ">Reajuste</span></a>


10 - ao abrir um card, vai clicar nessa opacao abaixo para marcar

<div class="actions pull-right"><button tabindex="-1" class="btn btn-primary vue-button btn-xs" type="button"><i class="fa fa-square"></i><span class="text-icon ">Considerar todos os trechos</span></button></div>

exatamente nessa caixa de selecao dele

<::before></::before>

11 - nesse input aqui vai encontrar taxas

<span class="select2-selection__rendered" id="select2-readjust_form_fee-container"><span class="select2-selection__placeholder">Selecione</span></span>


% Taxas adm.

especificamente esse nome acima para selecionar dentro do input

<span class="select2-selection__rendered" id="select2-readjust_form_fee-container" title="% Taxas adm."><span class="select2-selection__clear">×</span>% Taxas adm.</span>

12 - dentro desse campo abaixo, vai encontrar valor fixo e marcar

campo

<div class="col-sm-2-half"><div class="form-group radio_buttons required readjust_form_value_type radios-inline margin-top btn-align-input"><input type="hidden" name="readjust_form[value_type]" value="" autocomplete="off"><span class="radio inline"><div class="radio" id="uniform-readjust_form_value_type_percent"><span class="checked"><input class="radio_buttons required input-sm uniform" value="percent" type="radio" name="readjust_form[value_type]" id="readjust_form_value_type_percent"></span></div><label class="collection_radio_buttons" for="readjust_form_value_type_percent">%</label></span><span class="radio inline"><div class="radio" id="uniform-readjust_form_value_type_value"><span><input class="radio_buttons required input-sm uniform" value="value" type="radio" name="readjust_form[value_type]" id="readjust_form_value_type_value"></span></div><label class="collection_radio_buttons" for="readjust_form_value_type_value">Valor fixo</label></span></div></div>


local exato de valor fixo para clicar e marcar

<input class="radio_buttons required input-sm uniform" value="value" type="radio" name="readjust_form[value_type]" id="readjust_form_value_type_value">

13 - dentro desse input vai colocar um valor especifiico, deixe em um canto faciil para eu poder modiificar o valor que eu quiser

no caso atual vamos colocar o valor de 15
<input class="form-control string decimal optional input-sm allow-negative masked" data-precision="6" type="decimal" name="readjust_form[value]" id="readjust_form_value">


14 - apos isso vamos clicar nesse botao adicionar

<button tabindex="-1" class="btn btn-primary vue-button btn-align-input pull-right" name="add_fee" type="button"><i class="fa fa-plus"></i><span class="text-icon ">Adicionar</span></button>


15 - depois que adicionar, clicar no botao salvar

<button tabindex="-1" id="save-btn" type="submit" class="btn btn-primary vue-button"><i class="fa fa-save"></i><span class="text-icon ">Salvar</span></button>

16 - ao clicar em salvar abbbre um card pedindo confirmacao

<div aria-labelledby="swal2-title" aria-describedby="swal2-content" class="swal2-popup swal2-modal swal2-show" tabindex="-1" role="dialog" aria-live="assertive" aria-modal="true" style="display: flex;"><div class="swal2-header"><ul class="swal2-progress-steps" style="display: none;"></ul><div class="swal2-icon swal2-error" style="display: none;"><span class="swal2-x-mark"><span class="swal2-x-mark-line-left"></span><span class="swal2-x-mark-line-right"></span></span></div><div class="swal2-icon swal2-question" style="display: none;"></div><div class="swal2-icon swal2-warning swal2-animate-warning-icon" style="display: flex;"></div><div class="swal2-icon swal2-info" style="display: none;"></div><div class="swal2-icon swal2-success" style="display: none;"><div class="swal2-success-circular-line-left" style="background-color: rgb(255, 255, 255);"></div><span class="swal2-success-line-tip"></span> <span class="swal2-success-line-long"></span><div class="swal2-success-ring"></div> <div class="swal2-success-fix" style="background-color: rgb(255, 255, 255);"></div><div class="swal2-success-circular-line-right" style="background-color: rgb(255, 255, 255);"></div></div><img class="swal2-image" style="display: none;"><h2 class="swal2-title" id="swal2-title" style="display: flex;">Atenção!</h2><button type="button" class="swal2-close" aria-label="Close this dialog" style="display: none;">×</button></div><div class="swal2-content"><div id="swal2-content" style="display: block;">Confirma reajuste das taxas?</div><input class="swal2-input" style="display: none;"><input type="file" class="swal2-file" style="display: none;"><div class="swal2-range" style="display: none;"><input type="range"><output></output></div><select class="swal2-select" style="display: none;"></select><div class="swal2-radio" style="display: none;"></div><label for="swal2-checkbox" class="swal2-checkbox" style="display: none;"><input type="checkbox"><span class="swal2-label"></span></label><textarea class="swal2-textarea" style="display: none;"></textarea><div class="swal2-validation-message" id="swal2-validation-message"></div></div><div class="swal2-actions"><button type="button" class="swal2-confirm swal2-styled" aria-label="" style="display: inline-block; background-color: rgb(70, 117, 149); border-left-color: rgb(70, 117, 149); border-right-color: rgb(70, 117, 149);" id="swal-confirm">Sim</button><button type="button" class="swal2-cancel swal2-styled" aria-label="" style="display: inline-block;" id="swal-cancel">Cancelar</button></div><div class="swal2-footer" style="display: none;"></div></div>


voce vai clicar em sim para finalizar o primeiro processo

<button type="button" class="swal2-confirm swal2-styled" aria-label="" style="display: inline-block; background-color: rgb(70, 117, 149); border-left-color: rgb(70, 117, 149); border-right-color: rgb(70, 117, 149);" id="swal-confirm">Sim</button>


apos isso, vai voltar para a etapa 7

ponto crucial, essa etapa 7 ela clicou no item da primeira linha na coluna 10 dessa tabela que ja falei qual é, entao esse processo do 7 ate o 16 sera repetido, primeira repeticao ele faz na linha 1, segunda repeticao na linha 2, terceira repeticao na linha 3, até a linha 19, sao diversas paginas, e precisa esgotar ate ao final, chegando na ultima linha, neste caso da primeira pagina normalmente vai estar cheia, pois se precisar trocar de pagina quer dizer que terá 19 linhas, ele vai para o proximo passo ao repetir essa 19 vezes, ele vai para 


17 - essa linha aqui tera a opcao para passar para a proxima pagina

<div class="vue-paginated-table-footer vue-text-right"> <span class="margin-right"> <span>Qtd:&nbsp;</span> <select class="bg-white select input-sm"> <option value="auto">Auto</option> <option value="10">10</option> <option value="20">20</option> <option value="30">30</option> <option value="50">50</option> </select> </span> <span class="entries-info"> Exibindo 1 - 19 de 1147 </span>  <span class="btn-group vue-pagination-buttons margin-left"> <button type="button" class="btn btn-default" disabled=""><i class="fa fa-angle-double-left"></i></button> <button type="button" class="btn btn-default" disabled=""><i class="fa fa-angle-left"></i></button> <button type="button" class="vue-page-item btn btn-default blue-chambray"> 1 </button><button type="button" class="vue-page-item btn btn-default"> 2 </button><button type="button" class="vue-page-item btn btn-default"> 3 </button><button type="button" class="vue-page-item btn btn-default"> 4 </button><button type="button" class="vue-page-item btn btn-default"> 5 </button> <button type="button" class="btn btn-default"><i class="fa fa-angle-right"></i></button> <button type="button" class="btn btn-default"><i class="fa fa-angle-double-right"></i></button> </span>   </div>

especificamente nesse botao aqui
<button type="button" class="btn btn-default"><i class="fa fa-angle-right"></i></button>


ao clicar, ele vai para a proxima pagina, que vai ter mais linhas, ele vai voltar a fazer o loop

apos isso, vai voltar para a etapa 7 que irei refrisar abaixo

"ponto crucial, essa etapa 7 ela clicou no item da primeira linha na coluna 10 dessa tabela que ja falei qual é, entao esse processo do 7 ate o 16 sera repetido, primeira repeticao ele faz na linha 1, segunda repeticao na linha 2, terceira repeticao na linha 3, até a linha 19, sao diversas paginas, e precisa esgotar ate ao final, chegando na ultima linha, neste caso da primeira pagina normalmente vai estar cheia, pois se precisar trocar de pagina quer dizer que terá 19 linhas, ele vai para o proximo passo ao repetir essa 19 vezes, ele vai para"


apenas uma informacao para ter nocao, vc vai passar no estado atual de quantidade de conteudo que temos nessa tabela, sao Exibindo 1141 - 1147 de 1147, e ao final, quando chegar na ultima, n teremos provavelmente 19 linhas para vc fazer o processo acima, na ultima ao contar aqui tenho 7 linhas ate finalizar, mas pode ter menos, pode ter mais, pq a tabela sempre vai estar sendo populada, entao precisamos no script ter essa nocao


ao clicar na ultima linha e identificar que nao existe mais, encerramos o nosso processo finalmente, podemos encerrar o processo e o programa voltar ao estagio inicial antes de ser iniciado novamente e aguardar a proxima solicitacao



Como seu mentor, estruturarei este projeto de forma que ele deixe de ser um "script de cliques" e se torne uma **automação profissional e resiliente**.

Para rodar 1147 linhas sem supervisão, a estrutura deve prever falhas. Se o Selenium perder a conexão ou o site oscilar, o robô não pode simplesmente morrer; ele deve registrar o ocorrido e seguir adiante.

Abaixo, apresento o guia mestre em formato Markdown (`.md`) para você documentar seu projeto.

---

# Documentação do RPA: Reajuste de Tabelas de Preço

## 1. Estrutura de Arquivos Sugerida

Não coloque tudo em um único arquivo. Organize para facilitar a manutenção:

```text
projeto_rpa/
├── main.py              # Ponto de entrada (executa o loop principal)
├── config.py            # Variáveis editáveis (Valor do reajuste, credenciais, URLs)
├── bot_logic.py         # Funções do Selenium (clicar, preencher, extrair dados)
├── reports/
│   └── errors.log       # Registro técnico de falhas
└── logs/
    └── processamento.csv # Planilha com: Cliente, Status (Sucesso/Erro), Hora

```

---

## 2. Fluxo Estratégico de Operação

Este fluxo foca na **lógica de negócio** e na **resiliência**, ignorando IDs técnicos para facilitar o entendimento do processo.

### Fase A: Preparação e Filtro

1. **Login:** Acessa a plataforma e valida se a sessão está ativa.
2. **Navegação:** Segue o caminho: `Cadastros > Tabelas de Preço > Tabelas de Cliente`.
3. **Setup de Busca:** * Limpa filtros de filial pré-selecionados.
* Define "Ativa" como "Sim".
* Dispara a pesquisa inicial.



### Fase B: O Loop Mestre (Navegação Inteligente)

Este é o "cérebro" do robô. Em vez de contar até 19, ele pergunta à página: "Quantas linhas você tem agora?".

1. **Contagem Dinâmica:** O robô identifica todos os elementos da classe `.vue-item` na página atual.
2. **Iteração de Linha:** Para cada linha encontrada (seja 1 ou 19):
* **Tentativa (Try):** Inicia o processo de reajuste.
* **Captura (Except):** Se qualquer botão faltar ou o site travar, o robô tira um print da tela, salva o erro no log e pula para a próxima linha.


3. **Execução do Reajuste:**
* Acessa o menu lateral da linha.
* Seleciona "Reajuste".
* Marca "Considerar todos os trechos".
* Seleciona "% Taxas adm." no componente Select2.
* Define o tipo como "Valor Fixo".
* Insere o valor definido no `config.py` (Ex: 15).
* Salva e confirma no alerta (SweetAlert2).



### Fase C: Troca de Página

1. Após processar a última linha da página atual, o robô localiza o botão "Próxima Página" (`fa-angle-right`).
2. **Validação de Continuidade:** * Se o botão estiver clicável: Clica e reinicia a Fase B.
* Se o botão estiver bloqueado ou inexistente: Finaliza a automação.



---

## 3. Estratégia de Tratamento de Erros (Sniper de Falhas)

Para que o usuário possa intervir manualmente depois, o robô deve gerar um **Relatório de Pendências** ao final.

* **Identificador Único:** Ao falhar, salve o nome do Cliente ou o ID da linha.
* **Interface de Erro:** No final da execução, o script pode abrir um simples alerta em Python (usando `Tkinter` ou apenas um log no console) dizendo: *"Processamento concluído. 1140 sucessos, 7 falhas. Verifique o arquivo logs/processamento.csv"*.
* **O "Pulo do Gato":** Use **esperas explícitas** (`WebDriverWait`). Nunca use `time.sleep()`. O robô deve esperar o elemento "existir" para clicar. Se ele esperar 10 segundos e não aparecer, ele assume que deu erro na linha e passa para a próxima.

---

## 4. Por que usar `config.py`?

No seu código, no Passo 13, você mencionou que quer mudar o valor facilmente. No `config.py`, você deixará assim:

```python
# config.py
VALOR_REAJUSTE = "15"
TAXA_ALVO = "% Taxas adm."
DELAY_DIGITACAO = 0.1  # Segundos entre teclas para não bugar a máscara

```

Isso separa a **estratégia** (o que fazer) da **ferramenta** (como o Selenium clica).

---

### Diagnóstico de Mentor

O seu fluxo agora está robusto. O próximo passo crítico é a **identificação dos elementos Select2**. Como eles são dinâmicos (Vue.js), você precisará garantir que o robô clique no campo para abrir a lista antes de tentar selecionar o texto "% Taxas adm.".

**Você quer que eu detalhe como estruturar essa função específica para lidar com o Select2 e garantir que o valor "15" entre sem erros de formatação?**